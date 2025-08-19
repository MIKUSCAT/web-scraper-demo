"""
简化版Product Hunt爬虫演示程序
用于测试基本功能
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from loguru import logger
from src.scraper import RequestsScraper
from src.database import DataExporter
from src.models import ProductData

def demo_requests_scraper():
    """演示Requests爬虫（不依赖Playwright）"""
    logger.info("=== 简化版 Requests 爬虫演示 ===")
    
    scraper = RequestsScraper(delay=1.0)
    url = "https://www.producthunt.com/"
    
    logger.info(f"爬取页面: {url}")
    result = scraper.scrape_page(url)
    
    if result.success:
        logger.info(f"成功获取 {len(result.products)} 个产品")
        for i, product in enumerate(result.products[:3], 1):  # 只显示前3个
            logger.info(f"  {i}. {product.name}: {product.tagline}")
    else:
        logger.error(f"爬取失败: {result.error_message}")
    
    return result

def demo_data_export():
    """演示数据导出"""
    logger.info("=== 数据导出演示 ===")
    
    # 创建示例数据
    sample_data = [
        {
            "name": "示例产品1",
            "tagline": "这是一个示例产品",
            "votes": 100,
            "url": "https://example.com/1"
        },
        {
            "name": "示例产品2",
            "tagline": "另一个示例产品", 
            "votes": 50,
            "url": "https://example.com/2"
        }
    ]
    
    # 确保数据目录存在
    Path("data").mkdir(exist_ok=True)
    
    # 导出到JSON
    json_success = DataExporter.export_to_json(sample_data, "data/simple_demo_export.json")
    if json_success:
        logger.info("数据导出到JSON成功")
    
    # 导出到CSV
    csv_success = DataExporter.export_to_csv(sample_data, "data/simple_demo_export.csv")
    if csv_success:
        logger.info("数据导出到CSV成功")

def run_simple_demo():
    """运行简化演示"""
    logger.info("开始运行简化版Product Hunt爬虫演示程序")
    
    try:
        # 1. Requests爬虫演示
        result = demo_requests_scraper()
        
        # 2. 数据导出演示
        demo_data_export()
        
        # 3. 如果爬取成功，导出实际数据
        if result.success and result.products:
            logger.info("导出爬取到的实际数据...")
            products_data = []
            for product in result.products:
                products_data.append({
                    "name": product.name,
                    "tagline": product.tagline,
                    "url": str(product.url) if product.url else "",
                    "votes": product.votes or 0,
                    "scraped_at": product.scraped_at.isoformat()
                })
            
            # 导出实际爬取的数据
            DataExporter.export_to_json(products_data, "data/scraped_products.json")
            DataExporter.export_to_csv(products_data, "data/scraped_products.csv")
            logger.info("实际数据导出完成")
        
        logger.info("简化演示完成！")
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    # 导入日志配置
    from src.logger import setup_logger
    
    # 运行简化演示
    run_simple_demo()