"""文本分块：理解 chunk_size 和 chunk_overlap"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 300, chunk_overlap: int = 50) -> list:
    """
    将长文本分块
    
    Args:
        text: 原始长文本
        chunk_size: 每块最大字符数
        chunk_overlap: 相邻块重叠字符数
    
    Returns:
        文本块列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,  # 用字符数计量（中文适用）
        separators=["\n\n", "\n", "。", "；", " ", ""],  # 优先按段落切，再按句子切
    )
    
    chunks = splitter.split_text(text)
    return chunks


# ========== 测试 ==========
if __name__ == "__main__":
    # 模拟一篇研报摘要
    research_report = """
    新能源汽车行业深度报告
    
    一、行业概况
    2024年上半年，中国新能源汽车销量达到494.4万辆，同比增长32%。
    市场渗透率达到35.2%，较去年同期提升6个百分点。
    宁德时代继续保持全球动力电池装机量第一，市场份额达37.8%。
    
    二、政策支持
    工信部发布《新能源汽车产业发展规划（2024-2030年）》，
    明确到2030年新能源汽车新车销售量达到汽车新车销售总量的50%左右。
    地方政府陆续出台购车补贴、充电基础设施建设等配套政策。
    
    三、投资机会
    上游锂资源价格企稳回升，建议关注天齐锂业、赣锋锂业。
    中游电池环节竞争格局优化，宁德时代、比亚迪龙头地位稳固。
    下游整车品牌分化加剧，理想、蔚来等新势力销量增速放缓。
    充电桩运营商受益于政策推动，特来电、星星充电增长迅速。
    
    四、风险提示
    原材料价格波动风险、技术路线迭代风险、国际贸易摩擦风险。
     """
    
    chunks = split_text(research_report, chunk_size=200, chunk_overlap=30)
    
    print(f"原文长度: {len(research_report)} 字符")
    print(f"分块数量: {len(chunks)}")
    print("=" * 50)
    
    for i, chunk in enumerate(chunks):
        print(f"\n【块 {i+1}】长度: {len(chunk)}")
        print(chunk[:100] + "...")
