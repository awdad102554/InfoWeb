# 劳动仲裁信息查询综合服务平台

## 项目简介

本项目是将原有的 **Info**（内部API服务）和 **info-Web**（前端Web服务）两个项目整合为一个统一的Flask应用。

整合后的项目部署在 **10.99.144.x** 网段，同时提供：
1. 前端页面服务（劳动仲裁申请书在线填写、案件查询）
2. 内部API服务（企业信息查询、身份证信息查询）
3. 数据库API服务（案件数据增删改查）

## 项目结构

```
InfoWeb/
├── app.py                  # 主应用入口
├── start.py               # 启动脚本
├── start.bat              # Windows启动脚本
├── start.sh               # Linux/macOS启动脚本
├── requirements.txt       # Python依赖
├── README.md              # 说明文档
├── modules/               # 后端模块
│   ├── config.py          # 配置文件
│   ├── login_manager.py   # 登录管理
│   ├── company_query.py   # 企业查询
│   ├── id_card_query.py   # 身份证查询
│   └── database.py        # 数据库操作
├── static/                # 静态文件
│   ├── css/
│   │   └── styles.css     # 样式文件
│   └── js/
│       ├── scripts.js     # 主脚本
│       └── api_client.js  # API客户端
└── templates/             # HTML模板
    ├── index.html         # 劳动仲裁申请书在线填写页面
    └── query_test.html    # 案件查询测试页面
```

## 部署环境要求

- Python 3.8+
- MySQL 5.7+
- 部署网段：10.99.144.x

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：
- Flask==2.3.3
- Flask-CORS==4.0.0
- requests==2.31.0
- mysql-connector-python==8.1.0
- pymysql

### 2. 配置数据库

编辑 `modules/config.py`，修改数据库配置：

```python
DB_HOST = "10.99.144.29"      # 数据库主机
DB_PORT = 3306                # 数据库端口
DB_NAME = "劳动仲裁"           # 数据库名称
DB_USER = "root"              # 数据库用户
DB_PASSWORD = "difydify"      # 数据库密码
```

### 3. 启动服务

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

**或者直接使用Python:**
```bash
python start.py
```

### 4. 访问服务

服务启动后，可通过以下地址访问：

- **首页（劳动仲裁申请书在线填写）**: `http://<服务器IP>:5000/`
- **案件查询页面**: `http://<服务器IP>:5000/query`
- **API状态**: `http://<服务器IP>:5000/api/status`

## API接口列表

### 页面服务
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 劳动仲裁申请书在线填写页面 |
| GET | `/query` | 案件查询页面 |

### 内部API服务
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 服务状态检查 |
| GET | `/api/login/status` | 登录状态查询 |
| POST | `/api/login` | 手动登录 |
| POST | `/api/company/query` | 查询企业信息 |
| POST | `/api/idcard/query` | 查询身份证信息 |
| GET | `/api/db/status` | 数据库状态 |

### 案件管理API
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/cases/save` | 保存案件 |
| GET | `/api/cases/query` | 根据收件编号查询案件 |
| GET | `/api/cases/list` | 获取案件列表 |
| DELETE | `/api/cases/<id>` | 删除案件 |
| GET | `/api/cases/<id>/applicants` | 获取案件的申请人 |
| GET | `/api/cases/<id>/respondents` | 获取案件的被申请人 |
| GET | `/api/cases/<id>/evidence` | 获取案件的证据 |
| GET | `/api/applicants/<id>` | 获取申请人详情 |
| GET | `/api/applicants/<id>/requests` | 获取申请人的仲裁请求 |

## 配置说明

### 配置文件: `modules/config.py`

```python
class Config:
    # 数据库配置
    DB_HOST = "10.99.144.29"      # 数据库主机地址
    DB_PORT = 3306                # 数据库端口
    DB_NAME = "劳动仲裁"           # 数据库名称
    DB_USER = "root"              # 数据库用户名
    DB_PASSWORD = "difydify"      # 数据库密码
    
    # 外部API配置
    LOGIN_URL = "http://10.96.10.78:8080/v1/api/admin/login"
    COMPANY_QUERY_URL = "http://10.96.10.78:8080/v1/api/admin/datashare/openPlatformProxy/api/SJCK_businessFiveCertInfo"
    
    # 登录配置
    LOGIN_USERNAME = "huhailiang"
    LOGIN_PASSWORD = "..."
    
    # Flask配置
    FLASK_HOST = "0.0.0.0"        # 监听地址（0.0.0.0表示监听所有网卡）
    FLASK_PORT = 5000             # 服务端口
    FLASK_DEBUG = True            # 调试模式
```

## 数据库表结构

### 登录表 (login)
- 用户名、密码、authKey、sessionId、过期时间

### 企业信息缓存表 (company_cache)
- 企业名称、企业数据、创建时间、过期时间

### 个人信息缓存表 (idcard_cache)
- 身份证号、个人数据、创建时间、过期时间

### 案件相关表
- **cases**: 案件主表
- **applicants**: 申请人表
- **respondents**: 被申请人表
- **evidence**: 证据表
- **arbitration_requests**: 仲裁请求表

## 注意事项

1. **数据库初始化**: 首次启动时会自动创建所需的表结构
2. **登录过期**: 登录信息有效期为18小时，过期后自动重新登录
3. **缓存机制**: 企业信息和身份证查询结果会缓存30天
4. **端口占用**: 如果端口5000被占用，请修改config.py中的FLASK_PORT

## 故障排查

### 问题1: 端口被占用
```
错误: 端口 5000 已被占用
```
**解决方案**: 修改 `config.py` 中的 `FLASK_PORT` 为其他端口

### 问题2: 数据库连接失败
```
数据库连接失败: ...
```
**解决方案**: 检查config.py中的数据库配置是否正确

### 问题3: 缺少依赖
```
缺少依赖: No module named 'xxx'
```
**解决方案**: 运行 `pip install -r requirements.txt`

## 版本历史

### v1.0.0 (2026-02-12)
- 整合Info和info-Web两个项目
- 统一端口，简化部署
- 支持10.99.144.x网段部署

## 联系方式

如有问题，请联系技术支持。
