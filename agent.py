"""手写 ReAct Agent - 使用 DeepSeek API"""

import os
from dotenv import load_dotenv  
load_dotenv()  
import re
from typing import List, Dict, Optional
from tools import TOOL_REGISTRY, get_tool_description
from openai import OpenAI
import json
import time
from datetime import datetime
import threading


class ReActAgent:
    """
    ReAct 循环：Thought -> Action -> Observation -> ... -> Answer

    核心逻辑：
    1. 接收用户问题
    2. 构建 Prompt（包含工具描述 + 历史记录）
    3. 调用 LLM 获取 Thought + Action
    4. 解析 Action，执行对应工具
    5. 将 Observation 加入历史，继续循环
    6. 直到 LLM 输出 Answer 或达到最大步数
    """

    def __init__(self, max_steps: int = 10,memory_file:str = "agent_memory.json"):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        self.model = "deepseek-chat"
        self.max_steps = max_steps
        self.history: List[Dict] = []
        self.memory_file = memory_file
        self.conversation_history: List[Dict] = []
        self._load_memory()


    def _load_memory(self):
        """从文件加载历史记录"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data=json.load(f)
                    self.conversation_history = data.get("conversation_history",[])[-5:]
                    print(f"📚 已加载 {len(self.conversation_history)} 条历史记忆")
            except Exception as e:
                self.conversation_history = []
                print(f"⚠️ 加载历史记忆失败 - {e}")
        else:
            self.conversation_history = []
          

    def _save_memory(self,question:str,answer:str):
        """保存本次对话到文件"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data=json.load(f)
            else:
                data = {"conversation_history":[]}

            data["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer,
                "steps": self.history,
            })

            #写入文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {question} 的对话记忆")
        except Exception as e:
            print(f"⚠️ 保存对话记忆失败 - {e}")

    def _build_prompt(self, question: str) -> str:
        """
        构建给 LLM 的 Prompt

        包含：系统指令、工具描述、规则说明、示例、历史记录、当前问题
        """
        prompt = f"""你是一个智能量化助手，擅长获取数据、分析指标、执行回测。

{get_tool_description()}

规则：
1. 每一步你必须输出一个 JSON 对象，格式如下：
   {{
     "thought": "你的思考过程（用中文）",
     "action": "工具名",
     "action_input": "工具参数",
     "finish": false
   }}
2. 当得到最终答案时，输出：
   {{
     "thought": "已找到答案",
     "action": "",
     "action_input": "",
     "finish": true,
     "answer": "最终答案（用中文）"
   }}
3. 如果任务需要多个工具，按顺序调用，不要跳过步骤
4. 必须严格遵循 JSON 格式，不要输出 Markdown 代码块标记（```json），直接输出 JSON 字符串
5. 不要输出任何 JSON 以外的内容

单工具示例：
Question: 3 + 5 * 2 等于多少？
{{
  "thought": "这是一个数学计算，用计算器工具",
  "action": "calculator",
  "action_input": "3 + 5 * 2",
  "finish": false
}}
Observation: 13
{{
  "thought": "计算器返回了 13，这就是答案",
  "action": "",
  "action_input": "",
  "finish": true,
  "answer": "3 + 5 * 2 = 13"
}}

多工具协作示例：
Question: 帮我分析贵州茅台的股价
{{
  "thought": "需要先获取股票数据",
  "action": "get_stock_data",
  "action_input": "600519|20240101",
  "finish": false
}}
Observation: {{"股票代码": "600519", "最新收盘价": 1700.0, "MA5": 1680.5, "MA20": 1650.3}}
{{
  "thought": "有了数据，进一步做技术分析",
  "action": "analyze_stock",
  "action_input": "600519",
  "finish": false
}}
Observation: MA5 在 MA20 上方，RSI=45.2，处于中性区间
{{
  "thought": "已获取数据和分析，综合回答",
  "action": "",
  "action_input": "",
  "finish": true,
  "answer": "贵州茅台当前股价..."
}}

现在开始：
Question: {question}
"""
                # 追加历史记录（让 LLM 知道之前做过什么）—— 格式必须与示例一致！
        for step in self.history:
            # 从 "calculator[2+3]" 中解析出工具名和参数
            action_str = step['action']
            if '[' in action_str and action_str.endswith(']'):
                action_name = action_str.split('[')[0]
                action_input = action_str[action_str.index('[')+1:-1]
            else:
                action_name = action_str
                action_input = ""
            
            prompt += f'\n{{"thought": "{step["thought"]}", "action": "{action_name}", "action_input": "{action_input}", "finish": false}}\n'
            prompt += f'Observation: {step["observation"]}\n'

        if self.conversation_history:
            prompt += "\n\n之前的对话记录(供参考):\n"
            for conv in self.conversation_history[-3:]:
                prompt +=f"Q: {conv['question']}\nA: {conv['answer']}\n"

        return prompt

    def _call_llm(self, prompt: str,max_retries: int = 3) -> str:
        """调用 LLM，带重试和指数退避"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是遵循 ReAct 范式的智能助手。严格按照 Thought/Action/Answer 格式输出。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=500,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                wait_time = 2 ** attempt # 指数退避：1, 2, 4 秒
                print(f"⚠️ 调用 LLM 失败  ({attempt+1}/{max_retries}) :{e}")
                if attempt < max_retries - 1:
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)  # 指数退避，每次失败后等待 2^attempt 秒
                else:
                    #最终失败：返回json格式的错误答案
                    return json.dumps({
                        "thought":"LLM调用失败",
                        "action":"",
                        "action_input":"",
                        "finish":False,
                        "answer":f"抱歉，服务暂时不可用：{e}",
                    })

        return None



    def _parse_action(self, text: str) -> Optional[tuple]:
        """
        从 LLM 输出中解析 Action

        匹配格式：Action: tool_name[argument]
        返回：(tool_name, argument) 或 None
        """
        match = re.search(r'Action:\s*(\w+)\[(.*?)\]', text)
        if match:
            return match.group(1), match.group(2)
        return None

    def _extract_thought(self, text: str) -> str:
        """提取 Thought 内容"""
        match = re.search(r'Thought:\s*(.+?)(?=Action:|Answer:|$)', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _check_answer(self, text: str) -> Optional[str]:
        """
        检查是否得到最终答案

        匹配格式：Answer: xxx
        返回：xxx 或 None
        """
        match = re.search(r'Answer:\s*(.+)', text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _parse_llm_output(self, text: str) -> dict:
        """解析 LLM 输出为 JSON 字典"""
        cleaned =text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return {
                "thought": data.get("thought", ""),
                "action": data.get("action", ""),
                "action_input": data.get("action_input", ""),
                "finish": data.get("finish", False),
                "answer": data.get("answer", ""),
            }
        except json.JSONDecodeError:
            print(f"⚠️ JSON 解析失败，降级到文本解析: {text[:100]}...")
            return self._fallback_parse(text)

    def _fallback_parse(self, text: str) -> dict:
        """降级解析：兼容非 JSON 输出（保留 Day 1 的正则逻辑）"""
        # 先尝试从截断的 JSON 中提取关键字段
        try:
            # 匹配 "action": "xxx"
            action_match = re.search(r'"action"\s*:\s*"([^"]*)"', text)
            action = action_match.group(1) if action_match else ""
            
            # 匹配 "action_input": "xxx"
            input_match = re.search(r'"action_input"\s*:\s*"([^"]*)"', text)
            action_input = input_match.group(1) if input_match else ""
            
            # 匹配 "thought": "xxx"
            thought_match = re.search(r'"thought"\s*:\s*"([^"]*)"', text)
            thought = thought_match.group(1) if thought_match else ""
            
            # 匹配 "finish": true/false
            finish_match = re.search(r'"finish"\s*:\s*(true|false)', text, re.IGNORECASE)
            finish = finish_match.group(1).lower() == "true" if finish_match else False
            
            if action or finish:
                return {
                    "thought": thought,
                    "action": action,
                    "action_input": action_input,
                    "finish": finish,
                    "answer": "",
                }
        except Exception:
            pass
        
        # 如果上面失败，回退到原来的正则解析
        thought = self._extract_thought(text)
        action = self._parse_action(text)
        answer = self._check_answer(text)

        if answer:
            return {
                "thought": thought,
                "action": "",
                "action_input": "",
                "finish": True,
                "answer": answer,
            }
        elif action:
            return {
                "thought": thought,
                "action": action[0],
                "action_input": action[1],
                "finish": False,
                "answer": "",
            }
        else:
            return {
                "thought": thought,
                "action": "",
                "action_input": "",
                "finish": False,
                "answer": "",
            }
    def run(self, question: str) -> str:
        """执行 ReAct 循环"""
        print(f"🚀 任务: {question}")
        print("=" * 50)

        for step in range(self.max_steps):
            # 1. 构建 Prompt -> 调用 LLM
            prompt = self._build_prompt(question)
            llm_output = self._call_llm(prompt)

            print(f"\n[Step {step + 1}]")

            # 2. 解析json输出
            parsed = self._parse_llm_output(llm_output)
            
            if parsed["thought"]:
                print(f"🤔 Thought: {parsed['thought'][:150]}")

            # 3. 检查是否完成
            if parsed["finish"]:
                answer = parsed["answer"]
                print(f"✅ Answer: {parsed['answer']}")
                self._save_memory(question,answer)
                return answer

            # 4. 执行工具
            action_name = parsed["action"]
            action_input = parsed["action_input"]

            if action_name in TOOL_REGISTRY:
                print(f"🔧 Action: {action_name}[{action_input}]")

                # 工具调用（带重试）
                observation = None
                for retry in range(3):
                    try:
                        observation = TOOL_REGISTRY[action_name](action_input)
                        break
                    except Exception as e:
                        if retry < 2:
                            print(f"工具重试 {retry+1}/3...")
                            continue
                        observation = f"Error: 工具执行失败（重试3次） - {e}"
                
                if observation.startswith("Error:"):
                    print(f"❌ {observation[:200]}")
                    
            elif action_name:
                observation = f"Error: 未知工具 '{action_name}'"
                print(f"❌ {observation}")
            else:
                observation = f"Error: 未指定工具（可能是 JSON 解析失败）"
                print(f"❌ {observation}")

            # 截断过长的 Observation，防止 prompt 超限导致 LLM 输出截断
            MAX_OBS_LEN = 800
            if len(observation) > MAX_OBS_LEN:
                observation = observation[:MAX_OBS_LEN] + "\n...（内容已截断）"
            print(f"📊 Observation: {observation[:150]}...")

            # 6. 记录历史
            self.history.append({
                "thought": parsed["thought"],
                "action": f"{action_name}[{action_input}]" if action_name else "",
                "observation": observation,
            })

        # 达到最大步数仍未得到答案
        answer = "Answer: 达到最大步数，未能完成"
        self._save_memory(question,answer)
        return answer


# ========== 自检 ==========
if __name__ == "__main__":
    print("=== agent.py 自检 ===")
    print("ReActAgent 类已加载")
    print("下一步：运行 main.py 进行完整测试")
