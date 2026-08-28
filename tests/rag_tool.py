"""RAG 工具：封装研报问答，接入 Agent 工具系统"""
from report_qa import ReportQA
_qa_instance = None

def get_qa():
    global _qa_instance
    if _qa_instance is None:
        _qa_instance = ReportQA()
    return _qa_instance

def query_research_report(query: str) -> str:
    """
    查询研报知识库
    参数: 问题字符串
    返回: 基于研报的回答
    """
    try:
        qa = get_qa()
        return qa.answer(query,top_k=3)
    except Exception as e:
        return f"Error: 研报查询失败 - {str(e)}"

def search_report_chunks(query:str) -> str:
    """
    仅检索研报文本块（用于调试）
    参数: 查询字符串
    返回: 检索到的原始文本块
    """
    try:
        qa = get_qa()
        return qa.search_only(query,top_k=3)
    except Exception as e:
        return f"Error: 检索失败 - {str(e)}" 