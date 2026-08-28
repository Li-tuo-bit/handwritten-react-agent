"""精确调试 retrieve 方法"""

import os
from dotenv import load_dotenv
load_dotenv()

from chroma_manager import ChromaManager
from embedding_local import get_embedding_local

# 1. 连接数据库
db = ChromaManager()
collection = db.get_or_create_collection("research_reports")
print(f"集合数据条数: {collection.count()}")

# 2. 测试查询
query = "新能源汽车行业有哪些龙头公司？"
print(f"\n查询问题: {query}")

# 3. 生成查询向量
query_embedding = get_embedding_local([query])[0].tolist()
print(f"查询向量维度: {len(query_embedding)}")
print(f"查询向量前5个值: {query_embedding[:5]}")

# 4. 执行检索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
)

print(f"\nresults 类型: {type(results)}")
print(f"results keys: {results.keys()}")
print(f"results['ids']: {results['ids']}")
print(f"results['ids'] 长度: {len(results['ids'])}")
if results['ids'] and len(results['ids'][0]) > 0:
    print(f"第一个结果ID: {results['ids'][0][0]}")
    print(f"第一个结果distance: {results['distances'][0][0]}")
    print(f"第一个结果document前100字: {results['documents'][0][0][:100]}")
else:
    print("⚠️ 返回结果为空！")

# 5. 对比：用假向量查询
print("\n--- 对比：假向量查询 ---")
fake_embedding = [0.0] * len(query_embedding)
results_fake = collection.query(
    query_embeddings=[fake_embedding],
    n_results=3,
)
print(f"假向量返回 ids: {results_fake['ids']}")
