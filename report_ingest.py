"""研报入库：读取文本 → 分块 → 向量化 → 存入 ChromaDB"""

# 第1步：导入必要的库
import os
import glob
from uuid import uuid4

from chroma_manager import ChromaManager
from text_splitter import split_text
from  embedding_local import get_embedding_local

def load_reports_from_dir(report_dir: str = "./reports") -> list:
    """
    从目录加载所有研报文本文件
    
    Returns:
        列表，每项: {"filename": ..., "title": ..., "content": ..., "industry": ...}
    """
    reports = []

    # 遍历目录下所有 .txt 文件
    for filepath in glob.glob(os.path.join(report_dir, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(filepath)
        # 从文件名解析行业和日期，如 "新能源_2024Q2.txt"
        parts = filename.replace('.txt', '').split("_")
        industry = parts[0] if parts else "未知"
        date = parts[1] if len(parts) >1 else "未知"

        # 从内容第一行提取标题
        title =content.strip().split('\n')[0][:50]

        reports.append({
            "filename": filename,
            "title": title,
            "content": content,
            "industry": industry,
            "date": date,
        })
    print(f"📚 加载研报: {len(reports)} 篇")
    return reports

def ingest_reports_to_chroma(report_dir: str = "./reports",collection_name: str = "research_reports"):
    """
    研报入库主流程：分块 → 向量化 → 存入 ChromaDB
    """
    # 1. 初始化
    db = ChromaManager()
    collection = db.get_or_create_collection(collection_name)

    # 2. 加载研报
    reports = load_reports_from_dir(report_dir)

    # 3.逐篇处理
    total_chunks = 0

    for report in reports:
        print(f"\n📄 处理: {report['filename']} ({report['industry']})")
        
        # 3.1 分块
        chunks = split_text(report['content'], chunk_size=200, chunk_overlap=30)
        print(f"  分块: {len(chunks)} 块")

        # 3.2 向量化
        embeddings = get_embedding_local(chunks).tolist()

        # 3.3 准备元数据
        ids = [f"{report['filename']}_{uuid4().hex[:8]}" for _ in chunks]
        metadatas=[{
            "filename": report['filename'],
            "industry": report['industry'],
            "date": report['date'],
            "title": report['title'],
            "content": chunks[i],
        } for i in range(len(chunks))]

        # 3.4 入库
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

        total_chunks += len(chunks)
        print(f"  ✅ 入库完成")
    
    print(f"\n{'='*50}")
    print(f"总计: {len(reports)} 篇研报, {total_chunks} 个文本块")
    print(f"集合 '{collection_name}' 当前数量: {collection.count()}")

# ========== 入口 ==========
if __name__ == "__main__":
    ingest_reports_to_chroma()

