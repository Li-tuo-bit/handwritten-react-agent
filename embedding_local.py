"""本地 Embedding 方案——bge-small-zh"""

from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型（首次下载约 100MB，自动缓存）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

def get_embedding_local(texts: list) -> np.ndarray:
    """批量获取文本的 Embedding 向量"""
    # bge 模型推荐在查询前加 "represent this sentence for searching relevant passages:"
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings


def cosine_similarity(a, b) -> float:
    """计算两个向量的余弦相似度，范围 [-1, 1]，越接近 1 越相似"""
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
    
    embeddings = get_embedding_local(texts)
    
    print(f"向量维度: {embeddings.shape[1]}")
    print(f"白酒1 vs 白酒2 相似度: {cosine_similarity(embeddings[0], embeddings[1]):.4f}")
    print(f"白酒1 vs 新能源 相似度: {cosine_similarity(embeddings[0], embeddings[2]):.4f}")
