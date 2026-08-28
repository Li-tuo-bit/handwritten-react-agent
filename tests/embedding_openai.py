"""OpenAI Embedding 方案"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding_openai(text: str, model: str = "text-embedding-3-small") -> list:
    """获取文本的 Embedding 向量"""
    response = client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a, b) -> float:
    """计算两个向量的余弦相似度，范围 [-1, 1]，越接近 1 越相似"""
    import numpy as np
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ========== 测试 ==========
if __name__ == "__main__":
    texts = [
        "贵州茅台是中国高端白酒龙头企业",
        "五粮液是浓香型白酒的代表品牌",
        "宁德时代是全球最大的动力电池制造商",
    ]
    
    embeddings = [get_embedding_openai(t) for t in texts]
    
    print(f"向量维度: {len(embeddings[0])}")
    print(f"白酒1 vs 白酒2 相似度: {cosine_similarity(embeddings[0], embeddings[1]):.4f}")
    print(f"白酒1 vs 新能源 相似度: {cosine_similarity(embeddings[0], embeddings[2]):.4f}")
