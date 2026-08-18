"""手写 ReAct Agent - 使用 DeepSeek API"""

import os
import re
from typing import List, Dict, Optional
from tools import TOOL_REGISTRY, get_tool_description
from openai import OpenAI


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

    def __init__(self, max_steps: int = 10):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        self.model = "deepseek-chat"
        self.max_steps = max_steps
        self.history: List[Dict] = []

    def _build_prompt(self, question: str) -> str:
        """
        构建给 LLM 的 Prompt

        包含：系统指令、工具描述、规则说明、示例、历史记录、当前问题
        """
        prompt = f"""你是一个智能助手，通过交替思考和行动来解决问题。

{get_tool_description()}

规则：
- 先输出 Thought（思考），再输出 Action（行动）
- Thought 以 "Thought:" 开头
- Action 以 "Action:" 开头，格式：Action: tool_name[argument]
- 得到答案后输出 "Answer: 你的答案"
- 每次只输出一步 Thought 和 Action，不要一次输出多步

示例：
Question: 3 + 5 * 2 等于多少？
Thought: 这是一个数学计算，我应该用计算器工具。
Action: calculator[3 + 5 * 2]
Observation: 13
Thought: 计算器返回了 13，这就是最终答案。
Answer: 3 + 5 * 2 = 13

现在开始：
Question: {question}
"""
        # 追加历史记录（让 LLM 知道之前做过什么）
        for step in self.history:
            prompt += f"\nThought: {step['thought']}"
            prompt += f"\nAction: {step['action']}"
            prompt += f"\nObservation: {step['observation']}"

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用 DeepSeek API 获取 LLM 回复"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是遵循 ReAct 范式的智能助手。严格按照 Thought/Action/Answer 格式输出。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

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

    def run(self, question: str) -> str:
        """执行 ReAct 循环"""
        print(f"🚀 任务: {question}")
        print("=" * 50)

        for step in range(self.max_steps):
            # 1. 构建 Prompt -> 调用 LLM
            prompt = self._build_prompt(question)
            llm_output = self._call_llm(prompt)

            print(f"\n[Step {step + 1}]")

            # 2. 提取 Thought
            thought = self._extract_thought(llm_output)
            if thought:
                print(f"🤔 Thought: {thought[:150]}...")

            # 3. 检查是否得到最终答案
            answer = self._check_answer(llm_output)
            if answer:
                print(f"✅ Answer: {answer}")
                return answer

            # 4. 解析并执行 Action
            action = self._parse_action(llm_output)
            if not action:
                print(f"⚠️ 无法解析 Action，LLM 输出:\n{llm_output[:200]}")
                continue

            tool_name, tool_arg = action
            print(f"🔧 Action: {tool_name}[{tool_arg}]")

            # 5. 执行工具
            if tool_name in TOOL_REGISTRY:
                try:
                    observation = TOOL_REGISTRY[tool_name](tool_arg)
                except Exception as e:
                    observation = f"Error: 工具执行失败 - {e}"
            else:
                observation = f"Error: 未知工具 '{tool_name}'，可用工具: {list(TOOL_REGISTRY.keys())}"

            print(f"📊 Observation: {observation[:150]}...")

            # 6. 记录历史，进入下一轮
            self.history.append({
                "thought": thought,
                "action": f"{tool_name}[{tool_arg}]",
                "observation": observation,
            })

        # 达到最大步数仍未得到答案
        return "Answer: 达到最大步数，未能完成"


# ========== 自检 ==========
if __name__ == "__main__":
    print("=== agent.py 自检 ===")
    print("ReActAgent 类已加载")
    print("下一步：运行 main.py 进行完整测试")
