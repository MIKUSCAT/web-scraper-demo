"""
日志配置模块
"""
import sys
from pathlib import Path
from loguru import logger
from config.config import config

def setup_logger():
    """设置日志配置"""
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # 文件输出格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        colorize=True
    )
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 添加文件处理器 - 所有日志
    logger.add(
        log_dir / "app.log",
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # 添加错误日志文件处理器
    logger.add(
        log_dir / "error.log",
        format=file_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # 添加爬虫专用日志
    logger.add(
        log_dir / "scraper.log",
        format=file_format,
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        filter=lambda record: "scraper" in record["name"].lower()
    )
    
    logger.info("日志系统初始化完成")

# 自动初始化日志
setup_logger()