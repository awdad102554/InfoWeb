# 收件查询功能修复说明

## 问题诊断

### 1. 数据库连接问题
**现象**：日志频繁显示"数据库连接已断开，尝试重新连接"

**原因**：
- 原代码使用单例模式维持一个长连接
- MySQL 有连接超时限制，长时间不使用会自动断开
- 原 `_ensure_connection()` 检测机制不够健壮

**修复方案**：
- ✅ 使用连接池 (`MySQLConnectionPool`) 替代单例长连接
- ✅ 添加重试机制（最多 3 次）
- ✅ 每次操作后正确关闭连接，避免连接泄漏
- ✅ 连接池配置 `pool_reset_session=True`，每次归还连接时重置会话

### 2. 收件查询 API 数据结构不匹配
**现象**：前端页面无法正常显示查询结果

**原因**：
- API 返回的数据结构为 `{ data: { data: [...], totalNum: number, page: [offset, limit] } }`
- 原前端代码期望的是 `{ data: { list: [...], total: number } }`
- 内部 API 使用从 0 开始的页码，前端使用从 1 开始

**修复方案**：
- ✅ 更新前端代码适配实际 API 数据结构
- ✅ 后端转换页码：`page = page - 1`
- ✅ 优化页面显示，添加详情展开功能

### 3. 登录流程优化
**需求**：收件查询使用与企业查询/身份证查询相同的登录缓存机制

**实现方案**：
- ✅ 收件查询接口使用 `login_manager.check_and_renew_login()`
- ✅ 优先从数据库获取登录信息
- ✅ 如果不存在或过期，自动调用登录 API 并更新数据库
- ✅ 使用认证信息调用收件查询 API

## 登录流程说明

收件查询登录流程与企业查询、身份证查询一致：

```
┌─────────────────┐
│  收件查询请求    │
└────────┬────────┘
         ▼
┌───────────────────────────┐
│ login_manager.check_and_  │
│ renew_login()             │
└────────┬──────────────────┘
         ▼
┌──────────────────────────────┐     否      ┌──────────────────┐
│ 数据库中有有效登录信息？       │──────────▶│ 调用登录 API      │
└────────┬─────────────────────┘             └────────┬─────────┘
         │ 是                                       │
         ▼                                          ▼
┌──────────────────────┐               ┌──────────────────────┐
│ 加载登录信息到内存     │               │ 获取新认证信息        │
└────────┬─────────────┘               └──────────┬───────────┘
         │                                        │
         │          ┌─────────────────────────────┘
         │          ▼
         │   ┌──────────────────────┐
         └──▶│ 保存到数据库          │
             └────────┬─────────────┘
                      ▼
             ┌──────────────────────┐
             │ 获取认证头            │
             │ get_auth_headers()   │
             └────────┬─────────────┘
                      ▼
             ┌──────────────────────┐
             │ 调用收件查询 API      │
             └──────────────────────┘
```

## 文件修改列表

| 文件 | 修改内容 |
|------|----------|
| `modules/database.py` | 使用连接池 + 重试机制 |
| `modules/login_manager.py` | 添加异常处理，数据库失败可降级 |
| `modules/config.py` | 数据库地址改为 127.0.0.1 |
| `app.py` | 修复页码转换 `page - 1`，使用 check_and_renew_login |
| `templates/receive_query.html` | 全新设计，支持详情展开 |

## API 数据结构

### 请求参数
```
GET /api/receive/query
参数:
  - page: 页码（从1开始）
  - page_size: 每页数量
  - application_date: 申请日期（YYYY-MM-DD）
  - status: 状态（0-5）
  - case_no: 案件编号（如 202691）
```

### 响应结构
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "data": [
      {
        "id": 274494,
        "case_no": "明永劳人仲收[2026]91号",
        "status": 3,
        "application_at": "2026-02-09 00:00:00",
        "applicant": "李桂生",
        "applicant_arr": [...],
        "respondent": "三明美景建设有限公司",
        "respondent_arr": [...],
        "cases": {
          "case_reason": "社会保险争议",
          "case_source": "申请人窗口申请"
        },
        "groups": {
          "arbitrator": "胡海亮",
          "clerk": "陈文婷"
        },
        "review_opinion": "同意",
        "approval_opinion": "同意"
      }
    ],
    "totalNum": 2131,
    "page": [0, 3]
  }
}
```

## 状态码说明

| 状态值 | 含义 |
|--------|------|
| 0 | 收件登记 |
| 1 | 审核通过 |
| 2 | 审核不通过 |
| 3 | 审批通过 |
| 4 | 审批不通过 |
| 5 | 已提交 |

## 测试方法

### 1. 测试数据库连接
```bash
python -c "from modules.database import get_db_manager; db = get_db_manager(); print('OK')"
```

### 2. 测试登录缓存流程
```bash
python -c "
from login_manager import get_login_manager
login_mgr = get_login_manager()
result = login_mgr.check_and_renew_login()
print(f'登录检查结果: {result}')
"
```

### 3. 测试完整的收件查询
启动服务后访问：`http://localhost:5000/receive_query`

## 部署注意事项

1. **数据库配置**：确保 `modules/config.py` 中的数据库配置正确
   ```python
   DB_HOST = "127.0.0.1"  # 或实际的数据库IP
   DB_PORT = 3306
   DB_NAME = "判决书生成"
   DB_USER = "root"
   DB_PASSWORD = "difydify"
   ```

2. **网络连通性**：确保服务器能访问 `10.96.10.78:8080`（内部 API）

3. **依赖安装**：
   ```bash
   pip install mysql-connector-python requests
   ```

## 页面访问地址

- 收件查询页面：`http://<服务器IP>:5000/receive_query`
- 案件管理页面：`http://<服务器IP>:5000/cases`

## 日志说明

正常日志输出示例：
```
INFO:database:找到有效的登录信息: huhailiang
INFO:login_manager:已加载有效的登录信息
INFO:database:登录信息保存成功: huhailiang
INFO:login_manager:登录成功: huhailiang
```

如果看到以下日志，说明系统正在自动处理：
```
WARNING:database:获取连接失败 (尝试 1/3): ...
INFO:login_manager:登录已过期，重新登录...
INFO:login_manager:执行登录请求: huhailiang
```
