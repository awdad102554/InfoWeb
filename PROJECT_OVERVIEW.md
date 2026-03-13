# 劳动仲裁信息查询综合服务平台 - 项目总览

> 本文档供 AI 助手初始化后快速了解项目结构和功能

## 一、项目概述

### 1.1 项目简介
本项目是将原有的 **Info**（内部API服务）和 **info-Web**（前端Web服务）两个项目整合为一个统一的 Flask 应用。

### 1.2 核心功能
1. **前端页面服务** - 劳动仲裁申请书在线填写、案件查询
2. **内部API服务** - 企业信息查询、身份证信息查询
3. **数据库API服务** - 案件数据增删改查
4. **文档自动生成** - 根据案件数据自动填充 Word/Excel 模板生成仲裁文书

### 1.3 部署环境
- **部署网段**: 10.99.144.x
- **Python版本**: 3.8+
- **数据库**: MySQL 5.7+ (当前配置 127.0.0.1)
- **外部API**: http://10.96.10.78:8080 (仲裁系统内网)

---

## 二、项目结构

```
InfoWeb/
├── app.py                      # 主应用入口 (约2500行)
├── start.py                    # 启动脚本
├── start.sh / start.bat        # 启动脚本
├── requirements.txt            # Python依赖
├── database_schema.sql         # 数据库表结构
├── infoweb.service             # Linux系统服务配置
│
├── modules/                    # 后端模块
│   ├── config.py               # 配置文件
│   ├── login_manager.py        # 登录管理（Token缓存）
│   ├── company_query.py        # 企业信息查询
│   ├── id_card_query.py        # 身份证信息查询
│   └── database.py             # MySQL数据库操作（连接池）
│
├── templates/                  # HTML模板
│   ├── index.html              # 首页（申请书填写）
│   ├── query_test.html         # 案件查询测试
│   ├── cases_manage.html       # 案件管理
│   ├── receive_query.html      # 收件查询
│   ├── receive_detail.html     # 收件详情
│   ├── handle_query.html       # 立案查询
│   ├── handle_detail.html      # 立案详情
│   ├── reserve_query.html      # 预约仲裁查询
│   └── reserve_detail.html     # 预约仲裁详情
│
├── static/                     # 静态文件
│   ├── css/styles.css
│   └── js/
│       ├── scripts.js
│       └── api_client.js
│
├── 文件生成/                   # 文档模板和输出
│   ├── 1-立案/                 # 立案相关文书模板
│   ├── 2-开庭通知文书/         # 开庭通知模板
│   ├── 3-调、裁、决文书/       # 调解裁决文书模板
│   ├── 4-反申请文书/           # 反申请文书模板
│   ├── 5-撤诉文书/             # 撤诉文书模板
│   └── output/                 # 生成文件输出目录
│
├── document_generator.py       # 文档生成核心类
├── batch_document_generator.py # 批量文档生成
└── convert_doc_to_docx.py      # 格式转换工具
```

---

## 三、技术栈

| 类型 | 技术 |
|------|------|
| Web框架 | Flask 2.3.3 |
| 数据库 | MySQL 5.7+, mysql-connector-python 8.1.0 |
| HTTP请求 | requests 2.31.0 |
| 跨域支持 | Flask-CORS 4.0.0 |
| 文档处理 | python-docx 1.2.0, openpyxl 3.1.2, docxcompose 1.4.0 |
| 加密 | cryptography 3.0.0 |

---

## 四、核心模块详解

### 4.1 文档生成系统 (document_generator.py)

#### 核心类: `DocumentGenerator`

**功能**: 根据案件数据自动填充 Word/Excel 模板

**变量命名规范**:
```
基础字段:
- {case_no} / {case_no_raw}          # 案号
- {applicant} / {applicant_str}      # 申请人
- {respondent}                       # 被申请人（普通模板: 原始案件值; 多页模板: 当前页被申请人名字）
- {apply_at}                         # 申请日期
- {handle_at}                        # 立案日期
- {case_reason}                      # 案由
- {中文_today}                        # 今日中文日期

申请人信息:
- {applicant_arr[0].name}
- {applicant_arr[0].mobile}
- {applicant_arr[0].id_number}
- {applicant_arr[0].address}
- {applicant_arr[0].registered_permanent_residence}
- {applicant_arr[0].agents[0].name}
- {applicant_arr[0].agents[0].mobile}

被申请人信息:
- {respondent_arr[0].name}
- {respondent_arr[0].company_address}
- {respondent_arr[0].legal_name}
- {respondent_arr[0].legal_mobile}
- {respondent_arr[0].agents[0].name}
- {respondent_arr[0].agents[0].mobile}
- {respondent_arr[1].name} 至 {respondent_arr[9].name}  # 支持最多10个被申请人

被申请人动态表格行（立案审批表专用）:
- {respondent_table_row}                 # 触发变量，自动替换为"被申请人"或"被申请人1/2/3..."
  使用方式: 在表格行首单元格放置此变量，系统会根据被申请人数量自动复制行
  - 1个被申请人: 显示"被申请人"
  - 多个被申请人: 显示"被申请人1"、"被申请人2"、"被申请人3"...

仲裁请求:
- {request_numbers}                  # 请求编号列表 (1、2、3)
- {request_count}                    # 请求数量
- {request_1_intro}                  # 第1项请求内容
- {request_2_intro}                  # 第2项请求内容
- {request_1_object}                 # 第1项请求金额
- {total_money}                      # 案件标的总和

结案方式（调、裁、决文书送达回执专用）:
- {way}                              # 结案方式："调解"或"裁决"
  使用场景: 选择 3-调、裁、决文书 中的送达回执模板时
  获取优先级:
  1. 优先从案件数据 end_way 字段自动获取（已结案案件）
  2. end_way 为空或无效时，弹窗让用户选择
  可触发模板:
  - 03申请人送达回执调、裁、决定书3.docx
  - 03被申请人送达回执调、裁、决定书第三人3.docx
  - 05第三人送达回执3.docx

开庭信息 (从 tribunal_plan 提取):
- {open}                             # 开庭日期时间 (2026年3月11日（星期三）上午9时)
- {tel}                              # 开庭电话
- {年月日_created_at}                 # 开庭创建日期中文格式 (二〇二六年三月四日)

仲裁庭信息:
- {arbitrator}                       # 仲裁员（独任）
- {arbitrator_one}                   # 仲裁员一（合议庭）
- {arbitrator_two}                   # 仲裁员二（合议庭）
- {clerk}                            # 书记员

反申请信息（从 review_matter 中提取第一个包含"反申请"的记录）:
- {re_at_y}                          # 反申请年份，如 2026
- {re_at_m}                          # 反申请月份 1-12（无前导0）
- {re_at_d}                          # 反申请日期 1-31（无前导0）
- {中文_re_at}                       # 反申请日期中文格式，如 二零二五年十二月三十一日
- {re_applicant}                     # 反申请申请人（从第一个反申请记录的 applicant 字段获取）

多页生成模板（每页一个被申请人）:
触发条件: 必须同时满足以下三个条件：
1. 文件名同时包含"被申请人"且包含"送达回执"或"通知书"
2. 案件被申请人数量 > 1
3. 模板内容中实际包含 `{respondent}` 变量
- 满足条件: 每页对应一个被申请人，{respondent} 赋值为当前页被申请人名字，每页之间自动添加分页符
- 不满足条件: 生成单页文档

日期格式:
- {中文_apply_at}                     # 申请日期中文 (二〇二六年二月十三日)
- {中文_handle_at}                    # 立案日期中文
- {年月日_apply_at}                   # 申请日期年月日 (2026年2月13日)
- {年月日_handle_at}                  # 立案日期年月日
- {handle_at_y}                       # 立案日期年份，如 2026
- {handle_at_m}                       # 立案日期月份 1-12（无前导0）
- {handle_at_d}                       # 立案日期日 1-31（无前导0）

案号信息:
- {case_no} / {case_no_raw}           # 案号（如：永劳人仲案字[2026]123号）
- {case_no_year}                      # 案号年份部分（如：永劳人仲案字[2026]）
- {case_no_no}                        # 案号编号（如：123）

组合字符串变量（用于撤诉文书等）:
- {a_str}                             # 选中的申请人信息字符串
  格式: 申请人N：姓名，性别，民族，出生日期出生，身份证住址：XXX。公民身份号码：XXX。
  多申请人用换行分隔，除第一个外前面有两个全角空格缩进
- {r_str}                             # 被申请人信息字符串
  格式: 
  被申请人：XXX，统一社会信用代码: XXX，住所：XXX。
  　　法定代表人：XXX，职务。
```

**重要数据结构**:
- `tribunal_plan` - 开庭计划数组，包含字段: `open_at`, `text`, `tel`, `created_at`, `address`, `tribunal` 等

### 4.2 登录管理 (modules/login_manager.py)

**功能**: 管理仲裁系统的登录状态和 Token 缓存

**核心方法**:
- `check_and_renew_login()` - 检查并续期登录
- `get_auth_headers()` - 获取认证头

**流程**: 
1. 优先从数据库获取登录信息
2. 如不存在或过期，调用登录 API 获取新 Token
3. 保存到数据库供后续使用

### 4.3 数据库模块 (modules/database.py)

**功能**: MySQL 数据库连接池管理

**特点**:
- 使用 `MySQLConnectionPool` 连接池
- 带重试机制（最多3次）
- 自动表创建

**主要表**:
- `login_info` - 登录信息缓存
- `company_cache` - 企业信息缓存
- `idcard_cache` - 身份证信息缓存

---

## 五、API 接口列表

### 5.1 页面路由

| 路由 | 功能 |
|------|------|
| GET `/` | 首页（申请书填写） |
| GET `/query` | 案件查询页 |
| GET `/cases` | 案件管理页 |
| GET `/receive_query` | 收件查询页 |
| GET `/receive_detail` | 收件详情页 |
| GET `/handle_query` | 立案查询页 |
| GET `/handle_detail` | 立案详情页 |
| GET `/reserve_query` | 预约仲裁查询页 |
| GET `/reserve_detail` | 预约仲裁详情页 |

### 5.2 内部 API

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/status` | GET | 服务状态 |
| `/api/login/status` | GET | 登录状态 |
| `/api/login` | POST | 手动登录 |
| `/api/company/query` | POST | 企业信息查询 |
| `/api/idcard/query` | POST | 身份证信息查询 |
| `/api/db/status` | GET | 数据库状态 |

### 5.3 案件管理 API

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/cases/save` | POST | 保存案件 |
| `/api/cases/query` | GET | 根据收件编号查询 |
| `/api/cases/list` | GET | 案件列表 |
| `/api/cases/<id>` | GET/DELETE | 获取/删除案件 |
| `/api/cases/<id>/applicants` | GET | 获取申请人 |
| `/api/cases/<id>/respondents` | GET | 获取被申请人 |
| `/api/cases/<id>/evidence` | GET | 获取证据 |
| `/api/applicants/<id>` | GET | 申请人详情 |
| `/api/applicants/<id>/requests` | GET | 仲裁请求 |

### 5.4 外部数据查询 API（对接 10.96.10.78）

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/receive/query` | GET | 收件查询 |
| `/api/receive/detail` | GET | 收件详情 |
| `/api/handle/query` | GET | 立案查询 |
| `/api/handle/detail` | GET | 立案详情 |
| `/api/reserve/query` | GET | 预约仲裁查询 |
| `/api/reserve/detail` | GET | 预约仲裁详情 |

### 5.5 文档生成 API

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/doc_templates/tree` | GET | 获取模板树 |
| `/api/doc_templates/download` | GET | 下载模板 |
| `/api/doc_templates/generate` | POST | 生成文档 |

**生成文档请求示例**:
```json
{
  "template_paths": ["1-立案/（受理）立案审批表.docx"],
  "case_id": "215083"
}
```

---

## 六、数据流转图

```
┌─────────────────────────────────────────────────────────────┐
│                          用户请求                            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask Web 服务                          │
│                     (app.py :5000)                          │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
           ┌───────────────────────┐
           │    路由分发            │
           └───────────┬───────────┘
                       ▼
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│  页面路由   │  │  API 路由   │  │ 外部API代理 │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ templates/ │  │  MySQL DB  │  │10.96.10.78:│
│  HTML模板  │  │  (本地)    │  │   8080     │
└────────────┘  └────────────┘  └────────────┘
                       ▲
                       │
              ┌────────┴────────┐
              │  文档生成系统    │
              │document_generator│
              └─────────────────┘
```

---

## 七、配置文件说明 (modules/config.py)

```python
# 数据库配置
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "判决书生成"
DB_USER = "root"
DB_PASSWORD = "difydify"

# 外部仲裁系统API
LOGIN_URL = "http://10.96.10.78:8080/v1/api/admin/login"
COMPANY_QUERY_URL = "http://10.96.10.78:8080/v1/api/admin/datashare/..."

# 登录账号（已加密）
LOGIN_USERNAME = "huhailiang"
LOGIN_PASSWORD = "eyJpdiI6..."

# Flask配置
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# 缓存控制（app.py 中全局配置）
# 所有响应自动添加以下头部，禁止浏览器缓存动态内容：
# Cache-Control: no-cache, no-store, must-revalidate
# Pragma: no-cache
# Expires: 0
```

---

## 八、常见问题处理

### 8.1 数据库连接失败
- 检查 `modules/config.py` 中的数据库配置
- 确保 MySQL 允许远程连接
- 查看日志中的重试信息

### 8.2 外部 API 调用失败
- 检查是否能访问 `10.96.10.78:8080`
- 检查登录 Token 是否过期（会自动重新登录）
- 查看 `login_info` 表中的登录状态

### 8.3 文档生成变量为空
- 检查模板变量名是否正确（区分大小写）
- 检查 `tribunal_plan` 等数组字段是否有数据
- 查看日志中预处理后的数据输出

---

## 九、开发和调试

### 启动服务
```bash
# 开发模式
python start.py

# 或 Linux
./start.sh

# 或 Windows
start.bat
```

### 日志查看
- 日志输出到控制台和 `flask.log`
- 关键调试信息会打印预处理后的数据

### 测试接口
```bash
# 健康检查
curl http://localhost:5000/api/health

# 生成文档
curl -X POST http://localhost:5000/api/doc_templates/generate \
  -H "Content-Type: application/json" \
  -d '{"template_paths":["1-立案/（受理）立案审批表.docx"],"case_id":"215083"}'
```

---

## 十、扩展开发指南

### 添加新变量
1. 在 `document_generator.py` 的 `_preprocess_data` 方法中添加变量提取逻辑
2. 从 `case_data` 中获取原始数据
3. 处理格式转换（如日期转中文）
4. 赋值到 `result` 字典

### 添加新 API
1. 在 `app.py` 中添加路由装饰器
2. 调用 `login_manager.check_and_renew_login()` 获取认证
3. 使用 `requests` 调用外部 API
4. 返回统一格式的 JSON 响应

### 添加新模板
1. 将模板文件放入 `文件生成/` 下的对应分类目录
2. 使用 `{变量名}` 格式标记需要填充的位置
3. 确保变量名与代码中提取的变量一致

---

## 十一、开发协作规范

### Git 操作规范
**重要**: 在进行任何 git 操作前，必须获得用户的**明确指令**。

⚠️ **禁止以下行为**:
- 未经用户明确命令，不得执行 `git commit`
- 未经用户明确命令，不得执行 `git push`
- 未经用户明确命令，不得执行 `git merge`
- 未经用户明确命令，不得执行 `git rebase`
- 未经用户明确命令，不得执行 `git reset --hard`
- 未经用户明确命令，不得执行强制推送 (`git push --force`)

✅ **正确流程**:
1. 完成代码修改后，使用 `git status` 查看变更
2. 向用户汇报变更内容
3. 等待用户明确指令（如："提交并推送"）
4. 执行用户授权的 git 操作

💡 **说明**: 
- 即使用户在之前的对话中授权过提交，每次修改后仍需**重新确认**
- 用户明确说"提交"、"commit"、"push" 等关键词才算授权
- 不确定时，主动询问用户是否需要提交

---

## 十二、提交前文档更新规范

### 更新 PROJECT_OVERVIEW.md

**每次执行 `git commit` 前，必须先更新本文档**：

1. **在"关键文件修改历史"部分顶部添加新记录**（按时间倒序排列）
2. **记录格式**：`- **YYYY-MM-DD**: 修改内容简述（涉及文件、功能说明）`
3. **必须包含的信息**：
   - 修改日期
   - 修改内容简述
   - 涉及的文件（如 `app.py`, `document_generator.py` 等）
   - 功能/bug 的影响范围

**示例**：
```
- **2026-03-11**: 修复多页文档分页 bug，修正 `document_generator.py` 中 `doc._element` 访问方式，确保分页符正确插入到 sectPr 之前
```

**为什么需要这个规范**：
- 便于 LLM 模型（如 Kimi、Claude 等）快速了解项目最新变更
- 避免重复询问项目历史
- 帮助新加入的开发者快速上手

---

## 十三、关键文件修改历史

- **2026-03-13**: 添加裁决书制作功能，包括新增页面 `/award/make`、API 接口 `/api/award/elements/<case_id>`、数据库表 `裁决书要素保存`，支持裁决书要素的保存和查询（`app.py`, `templates/award_make.html`）
- **2026-03-13**: 将 `DatabaseManager._get_connection()` 改为公共方法 `get_connection()`，供裁决书 API 使用（`modules/database.py`）
- **2026-03-12**: 修复立案详情页状态显示问题，添加字符串类型状态映射（`templates/handle_detail.html`）
- **2026-03-12**: 修复立案查询等接口登录失效问题，添加401自动重新登录重试机制（`app.py`）
- **2026-03-12**: 调整立案查询界面表格列宽：序号40px、案件编号75px、被申请人80px、操作192px（`templates/handle_query.html`）
- **2026-03-12**: 立案查询案件编号显示优化，去除"明永劳人仲案字"前缀，只显示`[20XX]XX号`部分（`templates/handle_query.html`）
- **2026-03-11**: 添加全局缓存控制头，禁止浏览器缓存动态内容
- **2026-03-11**: 添加反申请相关变量 `{re_applicant}`（反申请申请人），从 `review_matter` 中第一个反申请记录获取
- **2026-03-11**: 修改多页生成分页条件，必须同时满足：文件名匹配、被申请人>1、**模板中包含 `{respondent}` 变量**，缺少变量则单页生成
- **2026-03-11**: 扩展多页生成模板匹配规则，文件名同时包含"被申请人"和"通知书"时也触发多页生成
- **2026-03-11**: 修复多页文档合并问题，使用手动添加分页符方式替代 Composer，确保每个被申请人内容独立成页
- **2026-03-11**: 修改 `{respondent}` 变量赋值逻辑，非多页模板时保持原始值，不覆盖为第一个被申请人名字
- **2026-03-11**: 修复多页文档分页 bug：修正 `doc._element` 访问方式，`doc._element` 是文档元素而非 body 元素，需使用 `doc._element[0]` 访问 body，解决分页符和内容被错误添加到 sectPr 之后导致的空白页问题
- **2026-03-11**: 优化结案方式 `{way}` 变量获取逻辑，优先从案件数据 `end_way` 字段自动获取（调解/裁决），无效时才需用户手动选择
- **2026-03-10**: 添加被申请人送达回执多页生成功能，文件名包含"被申请人"和"送达回执"时自动生成多页文档（每页一个被申请人）
- **2026-03-10**: 添加结案方式选择功能 `{way}`，支持调、裁、决文书送达回执模板二选一
- **2026-03-10**: 添加被申请人动态表格行功能 `{respondent_table_row}`，支持立案审批表自动复制多被申请人行
- **2026-03-10**: 扩展被申请人变量支持，最多支持10个被申请人 `{respondent_arr[0..9]}`
- **2026-03-06**: 添加组合字符串变量 `{a_str}`（选中申请人信息）和 `{r_str}`（被申请人信息）
- **2026-03-06**: 优化申请人选择功能：生成撤诉文书时多选申请人只生成一份文书
- **2026-03-05**: 添加立案日期变量 `{handle_at_y}`, `{handle_at_m}`, `{handle_at_d}`
- **2026-03-05**: 添加案号年份变量 `{case_no_year}`（从案号中提取年份）
- **2026-03-05**: 添加反申请日期变量 `{re_at_y}`, `{re_at_m}`, `{re_at_d}`, `{中文_re_at}`
- **2026-03-05**: 添加仲裁员和书记员变量 `{arbitrator}`, `{arbitrator_one}`, `{arbitrator_two}`, `{clerk}`
- **2026-03-05**: 修复 `年月日_created_at` 变量（ tribunal_plan 中字段名为 `created_at` 非 `create_at` ）
- **2026-03-04**: 添加批量文档生成功能
- **2026-03-03**: 添加立案查询和详情页面
- **2026-03-02**: 添加收件查询功能，修复数据库连接池

---

*文档更新时间: 2026-03-13 09:15*
