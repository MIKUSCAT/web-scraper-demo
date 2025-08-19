# Product Hunt 数据爬虫

一个功能完整的 Product Hunt 网站数据采集工具，支持多种爬虫引擎和数据库存储方案。

## 🚀 功能特性

- **多引擎支持**: 支持 Playwright 和 Requests 两种爬虫引擎
- **数据库集成**: 支持 PostgreSQL 和 MongoDB 数据存储
- **数据导出**: 支持 JSON 和 CSV 格式数据导出
- **异步处理**: 基于 asyncio 的高性能异步爬取
- **智能解析**: 自动识别和提取产品信息
- **错误处理**: 完善的错误处理和重试机制
- **日志记录**: 详细的日志记录和监控
- **配置灵活**: 支持环境变量和配置文件

## 📦 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/MIKUSCAT/web-scraper-demo.git
cd web-scraper-demo
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器（推荐）
```bash
playwright install chromium
```
> **注意**: 如果只想测试基础功能，可以跳过此步骤，直接运行简化版演示

### 4. 运行演示程序
```bash
# 运行简化版演示（推荐新手）
python simple_demo.py

# 运行完整演示（需要Playwright）
python demo.py
```

## 🎯 使用方法

### 基础演示
```bash
# 简化版演示 - 测试数据导出功能
python simple_demo.py

# 完整演示 - 包含Playwright爬虫（需要更长时间）
python demo.py
```

### 高级使用
```bash
# 使用默认配置运行主程序
python main.py

# 指定特定URL
python main.py --urls https://www.producthunt.com/ https://www.producthunt.com/topics/ai

# 使用不同的爬虫引擎
python main.py --engine requests

# 设置请求延迟
python main.py --delay 3.0
```

## 🗄️ 数据库配置（可选）

> **注意**: 数据库配置是可选的，程序默认会将数据导出为JSON和CSV文件

### PostgreSQL 配置
```bash
# 安装 PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# 从官网下载安装包: https://www.postgresql.org/download/windows/

# 创建数据库
sudo -u postgres createdb producthunt_data
```

### MongoDB 配置
```bash
# 安装 MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# Windows
# 从官网下载安装包: https://www.mongodb.com/try/download/community

# 启动 MongoDB 服务
sudo systemctl start mongod  # Linux
```

### 环境变量配置
创建 `.env` 文件（可选）：
```bash
# 数据库配置（可选）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=producthunt_data
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

MONGO_URI=mongodb://localhost:27017/
MONGO_DB=producthunt_data

# 爬虫配置
SCRAP_DELAY=2
TIMEOUT=30
HEADLESS=true
```

## 📊 数据结构

爬取的产品数据包含以下字段：

```python
{
    "name": "产品名称",
    "tagline": "产品标语/简介", 
    "description": "详细描述",
    "url": "产品链接",
    "votes": 投票数,
    "comments": 评论数,
    "maker": "制作者",
    "category": "分类",
    "launch_date": "发布日期",
    "image_url": "产品图片URL",
    "scraped_at": "采集时间",
    "source_url": "来源页面URL"
}
```

## 📁 输出文件

程序运行后会在以下位置生成文件：

```
data/
├── simple_demo_export.json     # 简化演示的示例数据
├── simple_demo_export.csv      # 简化演示的示例数据
├── scraped_products.json       # 实际爬取的产品数据
└── scraped_products.csv        # 实际爬取的产品数据

logs/
├── app.log                     # 应用日志
├── error.log                   # 错误日志
└── scraper.log                 # 爬虫专用日志
```

## 📁 项目结构

```
web-scraper-demo/
├── main.py                 # 主程序入口
├── demo.py                 # 完整演示程序
├── simple_demo.py          # 简化演示程序（推荐新手）
├── requirements.txt        # Python依赖
├── README.md              # 项目说明
├── config/
│   └── config.py          # 配置管理
├── src/
│   ├── models.py          # 数据模型
│   ├── scraper.py         # 爬虫引擎
│   ├── database.py        # 数据库操作
│   └── logger.py          # 日志配置
├── data/                  # 数据输出目录
└── logs/                  # 日志文件目录
```

## 🎨 使用示例

### 1. 基础爬取示例

```python
import asyncio
from src.scraper import ProductHuntScraper

async def basic_scrape():
    async with ProductHuntScraper() as scraper:
        result = await scraper.scrape_page("https://www.producthunt.com/")
        
        if result.success:
            print(f"获取到 {len(result.products)} 个产品")
            for product in result.products[:5]:
                print(f"- {product.name}: {product.tagline}")

asyncio.run(basic_scrape())
```

### 2. 数据库存储示例

```python
import asyncio
from src.database import DatabaseFactory
from src.models import ProductData

async def database_example():
    # 创建数据库管理器
    db_manager = DatabaseFactory.create_manager("postgresql")
    await db_manager.connect()
    
    # 创建示例产品
    product = ProductData(
        name="示例产品",
        tagline="这是一个示例",
        source_url="https://www.producthunt.com/"
    )
    
    # 保存到数据库
    await db_manager.save_products([product])
    
    # 获取数据
    products = await db_manager.get_products(limit=10)
    print(f"数据库中有 {len(products)} 个产品")
    
    await db_manager.disconnect()

asyncio.run(database_example())
```

### 3. 数据导出示例

```python
from src.database import DataExporter

# 示例数据
data = [
    {"name": "产品1", "votes": 100},
    {"name": "产品2", "votes": 50}
]

# 导出到JSON
DataExporter.export_to_json(data, "output.json")

# 导出到CSV
DataExporter.export_to_csv(data, "output.csv")
```

## 🚨 重要说明

### 网站反爬虫机制
Product Hunt 网站具有反爬虫机制：
- **简单HTTP请求会被阻止**（返回403错误）
- **推荐使用Playwright**进行爬取，可以绕过大部分限制
- **请合理设置延迟**，避免对服务器造成压力

### 使用建议
1. **新手用户**: 先运行 `simple_demo.py` 了解基本功能
2. **完整功能**: 安装Playwright后运行 `demo.py`
3. **遵守规则**: 请遵守网站的使用条款和robots.txt
4. **合理使用**: 仅用于学习和研究目的

## 🔍 故障排除

### 常见问题及解决方案

**1. 依赖安装失败**
```bash
# 如果pip安装失败，尝试升级pip
python -m pip install --upgrade pip

# 或者使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**2. Playwright 浏览器安装失败**
```bash
# 手动安装浏览器
playwright install chromium --force

# 如果网络问题，可以设置代理
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

**3. 爬取返回403错误**
- 这是正常现象，Product Hunt有反爬虫机制
- 使用Playwright可以解决此问题
- 简化版演示会显示此错误，但不影响其他功能测试

**4. 程序运行缓慢**
- Playwright首次启动需要较长时间
- 可以先运行简化版演示测试基础功能
- 调整延迟参数以平衡速度和稳定性

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 现代化的浏览器自动化
- [Requests](https://requests.readthedocs.io/) - 优雅的HTTP库
- [Loguru](https://loguru.readthedocs.io/) - 简化的日志记录
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证和设置管理

---

**免责声明**: 本工具仅供学习和研究使用，请遵守相关网站的使用条款和法律法规。使用者需自行承担使用风险。