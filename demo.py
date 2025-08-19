"""
Product Hunt 爬虫演示程序
简单的使用示例
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from loguru import logger
from src.scraper import ProductHuntScraper, RequestsScraper
from src.database import DatabaseFactory, DataExporter
from src.models import ProductData

async def demo_playwright_scraper():
    """演示Playwright爬虫"""
    logger.info("=== Playwright 爬虫演示 ===")
    
    urls = [
        "https://www.producthunt.com/",
        "https://www.producthunt.com/topics/artificial-intelligence"
    ]
    
    async with ProductHuntScraper(headless=True, delay=1.0) as scraper:
        for url in urls:
            logger.info(f"爬取页面: {url}")
            result = await scraper.scrape_page(url)
            
            if result.success:
                logger.info(f"成功获取 {len(result.products)} 个产品")
                for i, product in enumerate(result.products[:3], 1):  # 只显示前3个
                    logger.info(f"  {i}. {product.name}: {product.tagline}")
            else:
                logger.error(f"爬取失败: {result.error_message}")

def demo_requests_scraper():
    """演示Requests爬虫"""
    logger.info("=== Requests 爬虫演示 ===")
    
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

async def demo_database_operations():
    """演示数据库操作"""
    logger.info("=== 数据库操作演示 ===")
    
    # 创建示例数据
    sample_products = [
        ProductData(
            name="示例产品1",
            tagline="这是一个示例产品的描述",
            url="https://example.com/product1",
            votes=100,
            source_url="https://www.producthunt.com/"
        ),
        ProductData(
            name="示例产品2", 
            tagline="另一个示例产品",
            url="https://example.com/product2",
            votes=50,
            source_url="https://www.producthunt.com/"
        )
    ]
    
    # 尝试MongoDB（如果可用）
    try:
        logger.info("尝试连接MongoDB...")
        db_manager = DatabaseFactory.create_manager("mongodb")
        await db_manager.connect()
        
        # 保存数据
        success = await db_manager.save_products(sample_products)
        if success:
            logger.info("数据保存到MongoDB成功")
            
            # 获取数据
            products = await db_manager.get_products(limit=5)
            logger.info(f"从MongoDB获取了 {len(products)} 个产品")
            
            # 获取统计信息
            stats = await db_manager.get_stats()
            logger.info(f"MongoDB统计信息: {stats}")
            
        await db_manager.disconnect()
        
    except Exception as e:
        logger.warning(f"MongoDB操作失败: {e}")
    
    # 尝试PostgreSQL（如果可用）
    try:
        logger.info("尝试连接PostgreSQL...")
        db_manager = DatabaseFactory.create_manager("postgresql")
        await db_manager.connect()
        
        # 保存数据
        success = await db_manager.save_products(sample_products)
        if success:
            logger.info("数据保存到PostgreSQL成功")
            
            # 获取数据
            products = await db_manager.get_products(limit=5)
            logger.info(f"从PostgreSQL获取了 {len(products)} 个产品")
            
            # 获取统计信息
            stats = await db_manager.get_stats()
            logger.info(f"PostgreSQL统计信息: {stats}")
            
        await db_manager.disconnect()
        
    except Exception as e:
        logger.warning(f"PostgreSQL操作失败: {e}")

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
    json_success = DataExporter.export_to_json(sample_data, "data/demo_export.json")
    if json_success:
        logger.info("数据导出到JSON成功")
    
    # 导出到CSV
    csv_success = DataExporter.export_to_csv(sample_data, "data/demo_export.csv")
    if csv_success:
        logger.info("数据导出到CSV成功")

async def run_all_demos():
    """运行所有演示"""
    logger.info("开始运行Product Hunt爬虫演示程序")
    
    try:
        # 1. Playwright爬虫演示
        await demo_playwright_scraper()
        
        # 2. Requests爬虫演示
        demo_requests_scraper()
        
        # 3. 数据库操作演示
        await demo_database_operations()
        
        # 4. 数据导出演示
        demo_data_export()
        
        logger.info("所有演示完成！")
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")

if __name__ == "__main__":
    # 导入日志配置
    from src.logger import setup_logger
    
    # 运行演示
    asyncio.run(run_all_demos())