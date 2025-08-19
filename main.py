"""
Product Hunt 爬虫主程序
"""
import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from loguru import logger
from src.scraper import ProductHuntScraper, RequestsScraper
from src.database import DatabaseFactory, DataExporter
from src.models import ScrapingResult
from config.config import config

class ProductHuntCrawler:
    """Product Hunt 爬虫主类"""
    
    def __init__(self, use_playwright: bool = True, db_type: str = "postgresql"):
        self.use_playwright = use_playwright
        self.db_type = db_type
        self.db_manager = None
        
    async def initialize(self):
        """初始化爬虫"""
        logger.info("初始化Product Hunt爬虫...")
        
        # 初始化数据库管理器
        try:
            self.db_manager = DatabaseFactory.create_manager(self.db_type)
            await self.db_manager.connect()
            logger.info(f"数据库 ({self.db_type}) 连接成功")
        except Exception as e:
            logger.warning(f"数据库连接失败: {e}，将只保存到文件")
            self.db_manager = None
            
    async def cleanup(self):
        """清理资源"""
        if self.db_manager:
            await self.db_manager.disconnect()
            
    async def scrape_urls(self, urls: List[str]) -> List[ScrapingResult]:
        """爬取指定URL列表"""
        results = []
        
        if self.use_playwright:
            # 使用Playwright爬虫
            async with ProductHuntScraper(
                headless=config.HEADLESS,
                delay=config.SCRAP_DELAY
            ) as scraper:
                results = await scraper.scrape_multiple_pages(urls)
        else:
            # 使用Requests爬虫
            scraper = RequestsScraper(delay=config.SCRAP_DELAY)
            for url in urls:
                result = scraper.scrape_page(url)
                results.append(result)
                
        return results
        
    async def save_results(self, results: List[ScrapingResult]):
        """保存爬取结果"""
        all_products = []
        
        for result in results:
            if result.success:
                all_products.extend(result.products)
            else:
                logger.error(f"爬取失败: {result.page_url} - {result.error_message}")
                
        if not all_products:
            logger.warning("没有获取到任何产品数据")
            return
            
        logger.info(f"总共获取到 {len(all_products)} 个产品")
        
        # 保存到数据库
        if self.db_manager:
            success = await self.db_manager.save_products(all_products)
            if success:
                logger.info("数据已保存到数据库")
            else:
                logger.error("保存到数据库失败")
                
        # 保存到文件
        if config.SAVE_TO_FILE:
            # 确保数据目录存在
            Path(config.FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典格式
            products_dict = [product.dict() for product in all_products]
            
            if config.OUTPUT_FORMAT.lower() == 'json':
                DataExporter.export_to_json(products_dict, config.FILE_PATH)
            elif config.OUTPUT_FORMAT.lower() == 'csv':
                csv_path = config.FILE_PATH.replace('.json', '.csv')
                DataExporter.export_to_csv(products_dict, csv_path)
                
    async def run(self, urls: List[str]):
        """运行爬虫"""
        try:
            await self.initialize()
            
            logger.info(f"开始爬取 {len(urls)} 个页面")
            results = await self.scrape_urls(urls)
            
            await self.save_results(results)
            
            # 显示统计信息
            if self.db_manager:
                stats = await self.db_manager.get_stats()
                if stats:
                    logger.info(f"数据库统计: {stats}")
                    
            logger.info("爬取任务完成")
            
        except Exception as e:
            logger.error(f"爬取过程中出现错误: {e}")
            raise
        finally:
            await self.cleanup()

def get_default_urls() -> List[str]:
    """获取默认的Product Hunt URL列表"""
    return [
        "https://www.producthunt.com/",
        "https://www.producthunt.com/topics/developer-tools",
        "https://www.producthunt.com/topics/artificial-intelligence",
        "https://www.producthunt.com/topics/productivity",
        "https://www.producthunt.com/topics/design-tools"
    ]

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Product Hunt 数据爬虫")
    parser.add_argument(
        "--urls", 
        nargs="+", 
        help="要爬取的URL列表",
        default=get_default_urls()
    )
    parser.add_argument(
        "--engine", 
        choices=["playwright", "requests"], 
        default="playwright",
        help="爬虫引擎选择"
    )
    parser.add_argument(
        "--database", 
        choices=["postgresql", "mongodb"], 
        default="postgresql",
        help="数据库类型"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        default=True,
        help="无头模式运行浏览器"
    )
    parser.add_argument(
        "--delay", 
        type=float, 
        default=config.SCRAP_DELAY,
        help="请求间隔时间（秒）"
    )
    
    args = parser.parse_args()
    
    # 更新配置
    config.SCRAP_DELAY = args.delay
    config.HEADLESS = args.headless
    
    logger.info("=== Product Hunt 爬虫启动 ===")
    logger.info(f"爬虫引擎: {args.engine}")
    logger.info(f"数据库类型: {args.database}")
    logger.info(f"目标URL数量: {len(args.urls)}")
    logger.info(f"请求延迟: {args.delay}秒")
    
    # 创建并运行爬虫
    crawler = ProductHuntCrawler(
        use_playwright=(args.engine == "playwright"),
        db_type=args.database
    )
    
    try:
        await crawler.run(args.urls)
    except KeyboardInterrupt:
        logger.info("用户中断爬取")
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 导入日志配置
    from src.logger import setup_logger
    
    # 运行主程序
    asyncio.run(main())