from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer
import numpy as np

# 从 ModelScope 下载模型（国内源，自动缓存到 ./models 目录）
model_path = snapshot_download('BAAI/bge-small-zh-v1.5', cache_dir='./models')
print(f"模型已下载到: {model_path}")

# 加载本地模型
model = SentenceTransformer(model_path)

def get_embedding_local(texts: list) -> np.ndarray:
    """
    批量获取文本的 Embedding 向量
    texts: 字符串列表，如 ["句子1", "句子2"]
    """
    # normalize_embeddings=True 会让向量长度为1，方便后续计算相似度
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings

# 第四步：定义余弦相似度函数
def cosine_similarity(a,b) -> float:
    """
    计算两个向量的余弦相似度
    范围 [-1, 1]，越接近 1 表示越相似
    """
    a = np.array(a)
    b = np.array(b)

    # 点积 / (a的模 * b的模)
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ========== 测试 ==========
if __name__ == "__main__":
    texts = [
        "贵州茅台是中国高端白酒龙头企业",      # 白酒1
        "五粮液是浓香型白酒的代表品牌",        # 白酒2
        "宁德时代是全球最大的动力电池制造商",  # 新能源
    ]
    
    # 批量获取向量
    embeddings = get_embedding_local(texts)

    # 打印向量维度
    print(f"向量维度: {embeddings.shape[1]}")
    
    # 打印相似度（白酒 vs 白酒）
    sim_1_2 = cosine_similarity(embeddings[0], embeddings[1])
    print(f"白酒1 vs 白酒2 相似度: {sim_1_2:.4f}")
    
    # 打印相似度（白酒 vs 新能源）
    sim_1_3 = cosine_similarity(embeddings[0], embeddings[2])
    print(f"白酒1 vs 新能源 相似度: {sim_1_3:.4f}")