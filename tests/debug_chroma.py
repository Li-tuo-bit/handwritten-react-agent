# 保存为 debug_chroma.py，运行它
from chroma_manager import ChromaManager

db = ChromaManager()
collection = db.get_or_create_collection("research_reports")

print(f"集合里的数据条数: {collection.count()}")
print(f"前3条的 ID: {collection.get()['ids'][:3]}")
print(f"前3条的 metadata: {collection.get()['metadatas'][:3]}")

# 测试查询
query_embedding = [0.0] * 512  # 随便一个假向量，只看看能不能跑通
try:
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )
    print(f"查询返回的 keys: {results.keys()}")
    print(f"查询返回的 ids: {results['ids']}")
except Exception as e:
    print(f"查询报错: {e}")