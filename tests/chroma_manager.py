"""ChromaDB 向量数据库管理器"""

import os
import chromadb
from chromadb.config import Settings

class ChromaManager:
    """封装 ChromaDB 的常用操作"""    

    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        初始化 ChromaDB
        
        Args:
            persist_dir: 数据持久化目录，重启后数据仍在
        """ 
        self.persist_dir = persist_dir

        # 创建客户端（持久化模式）
        self.client = chromadb.PersistentClient(
            path= persist_dir,
            settings=Settings(anonymized_telemetry=False) #关闭遥测
        )

        print(f"✅ ChromaDB 已连接，存储目录: {persist_dir}")

    def get_or_create_collection(self, name: str):
        """获取或创建集合(类似SQL的表)"""
        return self.client.get_or_create_collection(name=name)

    def delete_collection(self,name: str):
        """删除集合"""
        try:
            self.client.delete_collection(name=name)
            print(f"🗑️ 集合 '{name}' 已删除")
        except Exception as e:
            print(f"⚠️ 删除失败: {e}")

    def list_collections(self):
        """列出所有集合"""
        return self.client.list_collections()

# ========== 测试 ==========
if __name__ == "__main__":
    db = ChromaManager()

    # 创建集合
    collection = db.get_or_create_collection("research_reports")
    print(f"集合数量: {collection.count()}")
    
    # 列出所有集合
    print(f"所有集合: {db.list_collections()}")
