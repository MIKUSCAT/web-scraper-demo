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

## 📦 安装依赖

### 1. 克隆项目
```bash
git clone <repository-url>
cd producthunt-scraper
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器
```bash
playwright install chromium
```

### 4. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库连接信息
```

## 🗄️ 数据库配置

### PostgreSQL 配置
```bash
# 安装 PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# 创建数据库
sudo -u postgres createdb producthunt_data
```

### MongoDB 配置
```bash
# 安装 MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# 启动 MongoDB 服务
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

## 🎯 使用方法

### 基本使用
```bash
# 使用默认配置运行
python main.py

# 指定特定URL
python main.py --urls https://www.producthunt.com/ https://www.producthunt.com/topics/ai

# 使用不同的爬虫引擎
python main.py --engine requests

# 使用不同的数据库
python main.py --database mongodb

# 设置请求延迟
python main.py --delay 3.0
```

### 演示程序
```bash
# 运行演示程序，测试所有功能
python demo.py
```

### 命令行参数

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--urls` | 要爬取的URL列表 | 默认URL集合 | 任意有效URL |
| `--engine` | 爬虫引擎 | playwright | playwright, requests |
| `--database` | 数据库类型 | postgresql | postgresql, mongodb |
| `--headless` | 无头模式 | True | True, False |
| `--delay` | 请求间隔(秒) | 2.0 | 任意正数 |

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

## 🔧 配置说明

### 环境变量配置 (.env)

```bash
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=producthunt_data
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

MONGO_URI=mongodb://localhost:27017/
MONGO_DB=producthunt_data

# 爬虫配置
SCRAP_DELAY=2
MAX_RETRIES=3
TIMEOUT=30
HEADLESS=true

# 输出配置
OUTPUT_FORMAT=json
SAVE_TO_FILE=true
FILE_PATH=./data/scraped_data.json
```

## 📁 项目结构

```
producthunt-scraper/
├── main.py                 # 主程序入口
├── demo.py                 # 演示程序
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
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

## 🚨 注意事项

1. **遵守网站规则**: 请遵守 Product Hunt 的 robots.txt 和使用条款
2. **合理设置延迟**: 建议设置适当的请求延迟，避免对服务器造成压力
3. **数据库权限**: 确保数据库用户有足够的权限创建表和插入数据
4. **网络环境**: 某些地区可能需要代理才能访问 Product Hunt
5. **浏览器依赖**: 使用 Playwright 时需要安装对应的浏览器

## 🔍 故障排除

### 常见问题

**1. Playwright 浏览器安装失败**
```bash
# 手动安装浏览器
playwright install chromium --force
```

**2. 数据库连接失败**
- 检查数据库服务是否启动
- 验证连接参数是否正确
- 确认用户权限是否足够

**3. 爬取数据为空**
- 检查目标网站是否可访问
- 验证页面结构是否发生变化
- 尝试增加请求延迟

**4. 内存使用过高**
- 减少并发数量
- 增加请求间隔
- 使用 requests 引擎替代 playwright

## 📈 性能优化

1. **并发控制**: 合理设置并发数量，避免过载
2. **缓存机制**: 对重复请求进行缓存
3. **数据库索引**: 为常用查询字段创建索引
4. **内存管理**: 及时释放不需要的对象
5. **日志级别**: 生产环境调整日志级别

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

**免责声明**: 本工具仅供学习和研究使用，请遵守相关网站的使用条款和法律法规。