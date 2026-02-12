# 劳动仲裁信息查询综合服务平台 - 部署说明

## 一、部署环境

- **服务器地址**: 10.99.144.x 网段
- **操作系统**: Windows Server / Linux
- **Python版本**: 3.8+
- **数据库**: MySQL 5.7+ (10.99.144.29)

## 二、快速部署

### 1. 复制项目到服务器

```bash
# 将整个 InfoWeb 文件夹复制到服务器
# 例如放在 D:\InfoWeb 或 /opt/infoweb
```

### 2. 安装Python依赖

```bash
cd InfoWeb
pip install -r requirements.txt
```

### 3. 检查数据库配置

编辑 `modules/config.py`:

```python
DB_HOST = "10.99.144.29"      # 数据库地址
DB_PORT = 3306                # 数据库端口
DB_USER = "root"              # 用户名
DB_PASSWORD = "difydify"      # 密码
```

### 4. 启动服务

**Windows:**
```bash
start.bat
```

**Linux:**
```bash
./start.sh
```

### 5. 验证服务

访问以下地址验证服务是否正常运行：

- 首页: `http://10.99.144.x:5000/`
- API状态: `http://10.99.144.x:5000/api/status`

## 三、服务管理

### Windows服务方式运行

创建Windows服务（使用nssm）:

```bash
nssm install LaborArbitrationService
# 设置路径: D:\InfoWeb\start.py
# 启动目录: D:\InfoWeb
```

### Linux后台运行

使用systemd或nohup:

```bash
# 使用nohup
nohup python start.py > app.log 2>&1 &

# 或使用systemd (创建 /etc/systemd/system/infoweb.service)
```

## 四、防火墙配置

确保服务器防火墙开放5000端口:

```bash
# Windows
netsh advfirewall firewall add rule name="InfoWeb" dir=in action=allow protocol=tcp localport=5000

# Linux
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

## 五、常见问题

### 1. 数据库连接失败

- 检查数据库服务器(10.99.144.29)是否可达
- 检查用户名密码是否正确
- 检查MySQL是否允许远程连接

### 2. 端口被占用

修改 `modules/config.py`:
```python
FLASK_PORT = 5001  # 改为其他端口
```

### 3. 外网访问不了

- 检查服务器防火墙
- 检查云服务商安全组规则
- 确认FLASK_HOST = "0.0.0.0"

## 六、API端点汇总

| 功能 | 地址 |
|------|------|
| 首页 | http://10.99.144.x:5000/ |
| 案件查询页 | http://10.99.144.x:5000/query |
| 服务状态 | http://10.99.144.x:5000/api/status |
| 企业信息查询 | POST http://10.99.144.x:5000/api/company/query |
| 身份证查询 | POST http://10.99.144.x:5000/api/idcard/query |
| 保存案件 | POST http://10.99.144.x:5000/api/cases/save |

## 七、技术支持

如有问题，请检查日志输出或联系技术支持。
