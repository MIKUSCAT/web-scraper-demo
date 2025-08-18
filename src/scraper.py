"""
Product Hunt 数据爬虫模块
"""
import asyncio
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from loguru import logger
from bs4 import BeautifulSoup
import requests

from models import ProductData, ScrapingResult
from config.config import config

class ProductHuntScraper:
    """Product Hunt 爬虫类"""
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        self.headless = headless
        self.delay = delay
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
        
    async def start(self):
        """启动浏览器"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.page = await self.browser.new_page()
            
            # 设置用户代理
            await self.page.set_extra_http_headers({
                'User-Agent': config.USER_AGENT
            })
            
            logger.info("浏览器启动成功")
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            raise
            
    async def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            logger.info("浏览器关闭成功")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
            
    async def scrape_page(self, url: str) -> ScrapingResult:
        """爬取指定页面的产品数据"""
        logger.info(f"开始爬取页面: {url}")
        
        try:
            # 访问页面
            await self.page.goto(url, wait_until='networkidle', timeout=config.TIMEOUT * 1000)
            await asyncio.sleep(self.delay)
            
            # 等待页面加载完成
            await self.page.wait_for_selector('[data-test="product-item"]', timeout=10000)
            
            # 获取页面内容
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 解析产品数据
            products = await self._parse_products(soup, url)
            
            result = ScrapingResult(
                success=True,
                products=products,
                total_count=len(products),
                page_url=url,
                scraped_at=datetime.now()
            )
            
            logger.info(f"成功爬取 {len(products)} 个产品")
            return result
            
        except Exception as e:
            logger.error(f"爬取页面失败: {e}")
            return ScrapingResult(
                success=False,
                products=[],
                total_count=0,
                page_url=url,
                scraped_at=datetime.now(),
                error_message=str(e)
            )
            
    async def _parse_products(self, soup: BeautifulSoup, source_url: str) -> List[ProductData]:
        """解析产品数据"""
        products = []
        
        # 查找产品容器
        product_items = soup.find_all('div', {'data-test': 'product-item'}) or \
                       soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
        
        if not product_items:
            # 尝试其他选择器
            product_items = soup.find_all('article') or \
                           soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['card', 'item', 'post']))
        
        logger.info(f"找到 {len(product_items)} 个产品项")
        
        for item in product_items:
            try:
                product = await self._extract_product_data(item, source_url)
                if product and product.name:  # 确保产品名称不为空
                    products.append(product)
            except Exception as e:
                logger.warning(f"解析产品数据失败: {e}")
                continue
                
        return products
        
    async def _extract_product_data(self, item_soup: BeautifulSoup, source_url: str) -> Optional[ProductData]:
        """从单个产品项中提取数据"""
        try:
            # 提取产品名称
            name_elem = item_soup.find('h3') or \
                       item_soup.find('h2') or \
                       item_soup.find('a', class_=lambda x: x and 'name' in x.lower()) or \
                       item_soup.find('div', class_=lambda x: x and 'title' in x.lower())
            
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # 提取标语/描述
            tagline_elem = item_soup.find('p') or \
                          item_soup.find('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['tagline', 'description', 'subtitle']))
            
            tagline = tagline_elem.get_text(strip=True) if tagline_elem else ""
            
            # 提取链接
            link_elem = item_soup.find('a', href=True)
            url = None
            if link_elem:
                href = link_elem['href']
                if href.startswith('http'):
                    url = href
                elif href.startswith('/'):
                    url = urljoin(source_url, href)
            
            # 提取投票数
            votes = 0
            vote_elem = item_soup.find('span', class_=lambda x: x and 'vote' in x.lower()) or \
                       item_soup.find('div', class_=lambda x: x and 'vote' in x.lower())
            
            if vote_elem:
                vote_text = vote_elem.get_text(strip=True)
                votes = self._extract_number(vote_text)
            
            # 提取评论数
            comments = 0
            comment_elem = item_soup.find('span', class_=lambda x: x and 'comment' in x.lower())
            if comment_elem:
                comment_text = comment_elem.get_text(strip=True)
                comments = self._extract_number(comment_text)
            
            # 提取图片URL
            img_elem = item_soup.find('img')
            image_url = None
            if img_elem and img_elem.get('src'):
                src = img_elem['src']
                if src.startswith('http'):
                    image_url = src
                elif src.startswith('/'):
                    image_url = urljoin(source_url, src)
            
            # 只有当产品名称不为空时才创建产品对象
            if name:
                return ProductData(
                    name=name,
                    tagline=tagline or "No description available",
                    url=url,
                    votes=votes,
                    comments=comments,
                    image_url=image_url,
                    source_url=source_url
                )
            
        except Exception as e:
            logger.warning(f"提取产品数据时出错: {e}")
            
        return None
        
    def _extract_number(self, text: str) -> int:
        """从文本中提取数字"""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
        
    async def scrape_multiple_pages(self, urls: List[str]) -> List[ScrapingResult]:
        """爬取多个页面"""
        results = []
        
        for url in urls:
            try:
                result = await self.scrape_page(url)
                results.append(result)
                
                # 延迟以避免被封
                await asyncio.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"爬取页面 {url} 失败: {e}")
                results.append(ScrapingResult(
                    success=False,
                    products=[],
                    total_count=0,
                    page_url=url,
                    error_message=str(e)
                ))
                
        return results

class RequestsScraper:
    """基于Requests的简单爬虫（备用方案）"""
    
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        
    def scrape_page(self, url: str) -> ScrapingResult:
        """爬取页面（同步版本）"""
        logger.info(f"使用Requests爬取页面: {url}")
        
        try:
            response = self.session.get(url, timeout=config.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = self._parse_products_simple(soup, url)
            
            time.sleep(self.delay)
            
            return ScrapingResult(
                success=True,
                products=products,
                total_count=len(products),
                page_url=url
            )
            
        except Exception as e:
            logger.error(f"Requests爬取失败: {e}")
            return ScrapingResult(
                success=False,
                products=[],
                total_count=0,
                page_url=url,
                error_message=str(e)
            )
            
    def _parse_products_simple(self, soup: BeautifulSoup, source_url: str) -> List[ProductData]:
        """简单的产品数据解析"""
        products = []
        
        # 查找标题和描述
        titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        
        for title in titles[:10]:  # 限制数量
            name = title.get_text(strip=True)
            if len(name) > 5:  # 过滤太短的标题
                # 查找相邻的描述
                description = ""
                next_elem = title.find_next(['p', 'div'])
                if next_elem:
                    description = next_elem.get_text(strip=True)[:200]  # 限制长度
                
                products.append(ProductData(
                    name=name,
                    tagline=description or "No description available",
                    source_url=source_url
                ))
                
        return products