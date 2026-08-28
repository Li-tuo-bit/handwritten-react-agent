"""对比 Embedding 方案"""

import time
from embedding_local import get_embedding_local, cosine_similarity

TEST_SENTENCES =[
    "贵州茅台发布半年报",
    "茅台集团召开股东大会",
    "宁德时代发布新电池技术",
    "比亚迪销量创新高",
]

# 计时
start =time.time()
embeddings = get_embedding_local(TEST_SENTENCES)
elapsed = time.time() - start

print(f"本地 bge-small-zh: {embeddings.shape[1]}维, 耗时 {elapsed:.2f}s")

# 对比相似度
print("\n语义相似度对比：")
sim_aa = cosine_similarity(embeddings[0],embeddings[1]) # 白酒 vs 白酒
sim_ab = cosine_similarity(embeddings[0],embeddings[2]) # 白酒 vs 新能源
print(f"白酒 vs 白酒: {sim_aa:.4f}")
print(f"白酒 vs 新能源: {sim_ab:.4f}")

# 思考题记录
print("\n观察记录：")
print("- 本地模型速度: 快/慢")
print("- 本地模型效果: 好/一般")
print("- 后续项目选择: 本地/OpenAI")
