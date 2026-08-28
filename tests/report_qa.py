"""研报问答：基于 ChromaDB 的 RAG 检索 + LLM 生成回答"""

# 第1步：导入必要的库
import os
from dotenv import load_dotenv  
load_dotenv()  

from chroma_manager import ChromaManager
from embedding_local import get_embedding_local
from langchain_openai import ChatOpenAI

class ReportQA:
    """研报问答系统"""

    def __init__(self,collection_name: str = "research_reports"):
        # 连接数据库
        self.db = ChromaManager()
        self.collection =self.db.get_or_create_collection(collection_name)

        # DeepSeek API（兼容 OpenAI 格式）
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
    def retrieve(self,query: str,top_k: int = 3,filter_industry: str = None) -> list:
        """
        检索相关文本块
        
        Args:
            query: 查询问题
            top_k: 返回前几块
            filter_industry: 按行业过滤，如 "新能源"
        """
        # 1. 查询向量化
        query_embedding = get_embedding_local([query])[0].tolist()

        # 2. 向量检索（修复：where=None 时不传 where 参数）
        if filter_industry:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"industry": filter_industry},
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
        
        # 3. 格式化结果
        retrieved = []
        for i in range(len(results["ids"][0])):
            retrieved.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        
        return retrieved

    def answer(self,query: str,top_k: int = 3) -> str:
        """
        完整问答流程：检索 → 构建 Prompt → LLM 生成回答
        """
        # 1. 检索
        retrieved = self.retrieve(query,top_k=top_k)

        if not retrieved:
            return "未找到相关研报内容。"

        # 2.构建上下文
        context = "\n\n---\n\n".join([
            f"【来源: {r['metadata']['title']} | {r['metadata']['industry']}】\n{r['text']}"
            for r in retrieved
        ])

        # 3. 构建 Prompt
        prompt = f"""你是一个专业的行业研究分析师。请基于以下研报内容回答问题。

研报内容：
{context}

用户问题：{query}

要求：
1. 基于研报内容回答，不要编造信息
2. 如果研报中没有相关信息，明确说明
3. 回答简洁，分点列出关键信息

回答："""
        
        # 4. 调用 LLM
        response = self.llm.invoke(prompt)
        return response.content

    def search_only(self,query: str,top_k: int = 3) -> str:
        """只检索，不调用 LLM，用于调试""" 
        retrieved = self.retrieve(query,top_k=top_k)

        lines = [f"检索结果(top{top_k}):"]
        for i,r in enumerate(retrieved):
            lines.append(f"\n[{i+1}] 相似度:{1-r['distance']:.4f}")
            lines.append(f"来源:{r['metadata']['title']} | {r['metadata']['industry']}")
            lines.append(f"内容:{r['text'][:150]}...")

        return "\n".join(lines)

# ========== 测试 ==========
if __name__ == "__main__":
    qa = ReportQA()
    
    # 测试 1：只检索
    print("="*60)
    print("测试 1：检索模式")
    print("="*60)
    result = qa.search_only("新能源电池产业链的投资机会")
    print(result)
    
    # 测试 2：完整问答
    print("\n" + "="*60)
    print("测试 2：问答模式")
    print("="*60)
    
    questions = [
        "新能源汽车行业有哪些龙头公司？",
        "白酒行业Q2的业绩怎么样？",
        "半导体行业的国产替代进展如何？",
        "宁德时代最近有什么新产品？",
        "消费板块现在能投资吗？",
    ]
    
    for q in questions:
        print(f"\n❓ Q: {q}")
        answer = qa.answer(q, top_k=3)
        print(f"💡 A: {answer}\n")
        print("-"*60)
            