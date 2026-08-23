"""最小可用 RAG 系统：文本 → 分块 → Embedding → 语义检索"""

import numpy as np
from text_splitter import split_text
from embedding_local import get_embedding_local, cosine_similarity

class SimpleRAG:
    def __init__(self):
        self.chunks = []    # 存文本块
        self.embeddings = []    # 存对应的向量

    def add_document(self,text: str):
        """添加文档：分块 → 向量化 → 存储"""
        # 1. 分块
        chunks = split_text(text,chunk_size=200,chunk_overlap=30)
        print(f"文档分块:{len(chunks)}块")

        # 2. 向量化（批量处理）
        embeddings = get_embedding_local(chunks).tolist()

        # 3. 存储（用 extend 把列表展开追加）
        self.chunks.extend(chunks)
        self.embeddings.extend(embeddings)
        print(f"总计存储:{len(self.chunks)}块")


    def search(self,query: str,top_k: int = 3) -> list:
        """语义检索"""
        if not self.chunks:
            return []

        # 1. 向量化查询
        query_embedding = get_embedding_local([query])[0]

        # 2. 计算相似度
        similarities = []
        for emb in self.embeddings:
            sim = cosine_similarity(query_embedding,emb)
            similarities.append(sim)

        # 3. 排序取Top K
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "chunk": self.chunks[idx],
                "score": float(similarities[idx]),
            })

        return results

# ========== 测试 ==========
if __name__ == "__main__":
    rag = SimpleRAG()
    
    # 添加 3 篇研报
    reports = {
        "新能源":"""新能源汽车行业报告：2024年销量增长32%，宁德时代全球装机量第一。
        上游锂资源价格企稳，建议关注天齐锂业、赣锋锂业。
        充电桩运营商特来电、星星充电增长迅速。""",
        "消费":"""白酒行业报告：贵州茅台Q2营收增长17%，五粮液渠道改革见效。
        高端白酒需求韧性较强，宴席场景恢复带动动销改善。
        建议关注贵州茅台、五粮液、泸州老窖。""",
        "科技":"""半导体行业报告：AI芯片需求爆发，英伟达供应链紧张。
        国内厂商寒武纪、海光信息加速追赶，但制程仍落后2-3代。
        设备厂商北方华创订单饱满。""",
    }
    
    for name, content in reports.items():
        print(f"\n加载研报: {name}")
        rag.add_document(content)
    
    # 测试查询
    queries = [
        "消费板块有什么投资机会？",
        "新能源电池产业链怎么样？",
        "AI芯片相关公司有哪些？",
    ]
    
    for q in queries:
        print(f"\n{'='*50}")
        print(f"查询: {q}")
        print("="*50)
    
        results = rag.search(q, top_k=2)
        for i, r in enumerate(results):
            print(f"\nTop {i+1} (相似度: {r['score']:.4f}):")
            print(r['chunk'][:150] + "...")