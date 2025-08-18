"""
配置管理模块
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 数据库配置
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'producthunt_data')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'producthunt_data')
    
    # 爬虫配置
    SCRAP_DELAY = float(os.getenv('SCRAP_DELAY', 2.0))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    
    # 输出配置
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'json')
    SAVE_TO_FILE = os.getenv('SAVE_TO_FILE', 'true').lower() == 'true'
    FILE_PATH = os.getenv('FILE_PATH', './data/scraped_data.json')
    
    # Playwright配置
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    @property
    def postgres_url(self) -> str:
        """获取PostgreSQL连接URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        required_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD']
        for var in required_vars:
            if not os.getenv(var):
                print(f"警告: 环境变量 {var} 未设置")
                return False
        return True

# 全局配置实例
config = Config()