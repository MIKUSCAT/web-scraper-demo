"""
数据模型定义
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class ProductData(BaseModel):
    """Product Hunt产品数据模型"""
    
    name: str = Field(..., description="产品名称")
    tagline: str = Field(..., description="产品标语/简介")
    description: Optional[str] = Field(None, description="详细描述")
    url: Optional[HttpUrl] = Field(None, description="产品链接")
    votes: Optional[int] = Field(None, description="投票数")
    comments: Optional[int] = Field(None, description="评论数")
    maker: Optional[str] = Field(None, description="制作者")
    category: Optional[str] = Field(None, description="分类")
    launch_date: Optional[datetime] = Field(None, description="发布日期")
    image_url: Optional[HttpUrl] = Field(None, description="产品图片URL")
    
    # 元数据
    scraped_at: datetime = Field(default_factory=datetime.now, description="采集时间")
    source_url: HttpUrl = Field(..., description="来源页面URL")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScrapingResult(BaseModel):
    """爬取结果模型"""
    
    success: bool = Field(..., description="是否成功")
    products: List[ProductData] = Field(default_factory=list, description="产品列表")
    total_count: int = Field(0, description="总数量")
    page_url: HttpUrl = Field(..., description="页面URL")
    scraped_at: datetime = Field(default_factory=datetime.now, description="采集时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    
class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    
    db_type: str = Field(..., description="数据库类型 (postgres/mongodb)")
    connection_params: Dict[str, Any] = Field(..., description="连接参数")
    table_name: Optional[str] = Field("products", description="表名/集合名")