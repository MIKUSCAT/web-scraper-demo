"""
数据库存储模块
支持PostgreSQL和MongoDB
"""
import asyncio
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json

import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from pymongo.collection import Collection
from loguru import logger

from models import ProductData, ScrapingResult
from config.config import config

class DatabaseManager:
    """数据库管理器基类"""
    
    def __init__(self):
        self.connection = None
        
    async def connect(self):
        """连接数据库"""
        raise NotImplementedError
        
    async def disconnect(self):
        """断开数据库连接"""
        raise NotImplementedError
        
    async def save_products(self, products: List[ProductData]) -> bool:
        """保存产品数据"""
        raise NotImplementedError
        
    async def get_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取产品数据"""
        raise NotImplementedError

class PostgreSQLManager(DatabaseManager):
    """PostgreSQL数据库管理器"""
    
    def __init__(self):
        super().__init__()
        self.connection = None
        
    async def connect(self):
        """连接PostgreSQL数据库"""
        try:
            self.connection = psycopg2.connect(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                database=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                cursor_factory=RealDictCursor
            )
            
            # 创建表
            await self._create_tables()
            logger.info("PostgreSQL连接成功")
            
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            raise
            
    async def _create_tables(self):
        """创建数据表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            tagline TEXT,
            description TEXT,
            url VARCHAR(500),
            votes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            maker VARCHAR(255),
            category VARCHAR(100),
            launch_date TIMESTAMP,
            image_url VARCHAR(500),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_url VARCHAR(500) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
        CREATE INDEX IF NOT EXISTS idx_products_scraped_at ON products(scraped_at);
        CREATE INDEX IF NOT EXISTS idx_products_votes ON products(votes DESC);
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.connection.commit()
            logger.info("数据表创建成功")
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            raise
            
    async def disconnect(self):
        """断开PostgreSQL连接"""
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL连接已关闭")
            
    async def save_products(self, products: List[ProductData]) -> bool:
        """保存产品数据到PostgreSQL"""
        if not products:
            return True
            
        insert_sql = """
        INSERT INTO products (
            name, tagline, description, url, votes, comments, 
            maker, category, launch_date, image_url, scraped_at, source_url
        ) VALUES (
            %(name)s, %(tagline)s, %(description)s, %(url)s, %(votes)s, %(comments)s,
            %(maker)s, %(category)s, %(launch_date)s, %(image_url)s, %(scraped_at)s, %(source_url)s
        ) ON CONFLICT (name, source_url) DO UPDATE SET
            tagline = EXCLUDED.tagline,
            description = EXCLUDED.description,
            votes = EXCLUDED.votes,
            comments = EXCLUDED.comments,
            updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            with self.connection.cursor() as cursor:
                for product in products:
                    product_dict = product.dict()
                    # 处理datetime对象
                    if product_dict.get('launch_date'):
                        product_dict['launch_date'] = product_dict['launch_date']
                    if product_dict.get('scraped_at'):
                        product_dict['scraped_at'] = product_dict['scraped_at']
                    
                    cursor.execute(insert_sql, product_dict)
                    
                self.connection.commit()
                logger.info(f"成功保存 {len(products)} 个产品到PostgreSQL")
                return True
                
        except Exception as e:
            logger.error(f"保存产品数据失败: {e}")
            self.connection.rollback()
            return False
            
    async def get_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从PostgreSQL获取产品数据"""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM products ORDER BY scraped_at DESC"
                if limit:
                    sql += f" LIMIT {limit}"
                    
                cursor.execute(sql)
                results = cursor.fetchall()
                
                # 转换为字典列表
                products = [dict(row) for row in results]
                logger.info(f"从PostgreSQL获取了 {len(products)} 个产品")
                return products
                
        except Exception as e:
            logger.error(f"获取产品数据失败: {e}")
            return []
            
    async def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_products,
                        COUNT(DISTINCT source_url) as unique_sources,
                        MAX(scraped_at) as last_scraped,
                        AVG(votes) as avg_votes
                    FROM products
                """)
                
                result = cursor.fetchone()
                return dict(result) if result else {}
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

class MongoDBManager(DatabaseManager):
    """MongoDB数据库管理器"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.db = None
        self.collection = None
        
    async def connect(self):
        """连接MongoDB数据库"""
        try:
            self.client = MongoClient(config.MONGO_URI)
            self.db = self.client[config.MONGO_DB]
            self.collection = self.db.products
            
            # 创建索引
            await self._create_indexes()
            logger.info("MongoDB连接成功")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
            
    async def _create_indexes(self):
        """创建索引"""
        try:
            self.collection.create_index("name")
            self.collection.create_index("scraped_at")
            self.collection.create_index([("votes", -1)])
            self.collection.create_index([("name", 1), ("source_url", 1)], unique=True)
            logger.info("MongoDB索引创建成功")
        except Exception as e:
            logger.warning(f"创建索引失败: {e}")
            
    async def disconnect(self):
        """断开MongoDB连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
            
    async def save_products(self, products: List[ProductData]) -> bool:
        """保存产品数据到MongoDB"""
        if not products:
            return True
            
        try:
            documents = []
            for product in products:
                doc = product.dict()
                # 处理datetime对象
                if doc.get('scraped_at'):
                    doc['scraped_at'] = doc['scraped_at']
                if doc.get('launch_date'):
                    doc['launch_date'] = doc['launch_date']
                documents.append(doc)
            
            # 使用upsert操作
            for doc in documents:
                self.collection.update_one(
                    {"name": doc["name"], "source_url": doc["source_url"]},
                    {"$set": doc},
                    upsert=True
                )
                
            logger.info(f"成功保存 {len(products)} 个产品到MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"保存产品数据失败: {e}")
            return False
            
    async def get_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从MongoDB获取产品数据"""
        try:
            cursor = self.collection.find().sort("scraped_at", -1)
            if limit:
                cursor = cursor.limit(limit)
                
            products = list(cursor)
            
            # 处理ObjectId
            for product in products:
                if '_id' in product:
                    product['_id'] = str(product['_id'])
                    
            logger.info(f"从MongoDB获取了 {len(products)} 个产品")
            return products
            
        except Exception as e:
            logger.error(f"获取产品数据失败: {e}")
            return []
            
    async def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_products": {"$sum": 1},
                        "unique_sources": {"$addToSet": "$source_url"},
                        "avg_votes": {"$avg": "$votes"},
                        "last_scraped": {"$max": "$scraped_at"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_products": 1,
                        "unique_sources": {"$size": "$unique_sources"},
                        "avg_votes": 1,
                        "last_scraped": 1
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

class DatabaseFactory:
    """数据库工厂类"""
    
    @staticmethod
    def create_manager(db_type: str) -> DatabaseManager:
        """创建数据库管理器"""
        if db_type.lower() == 'postgresql':
            return PostgreSQLManager()
        elif db_type.lower() == 'mongodb':
            return MongoDBManager()
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

class DataExporter:
    """数据导出器"""
    
    @staticmethod
    def export_to_json(products: List[Dict[str, Any]], file_path: str) -> bool:
        """导出数据到JSON文件"""
        try:
            # 处理datetime对象
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2, default=json_serializer)
                
            logger.info(f"数据已导出到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return False
            
    @staticmethod
    def export_to_csv(products: List[Dict[str, Any]], file_path: str) -> bool:
        """导出数据到CSV文件"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(products)
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            logger.info(f"数据已导出到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return False