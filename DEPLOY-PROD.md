# 生产环境部署指南

## 方案一：使用Gunicorn（Linux推荐）

### 1. 安装生产环境依赖

```bash
cd /vol2/1000/python-project/InfoWeb
source venv/bin/activate
pip install gunicorn
```

### 2. 启动生产服务器

```bash
./start-prod.sh
```

或手动指定参数：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

参数说明：
- `-w 4`: 4个工作进程（建议设为 CPU核心数*2+1）
- `-b 0.0.0.0:5000`: 绑定地址和端口
- `--timeout 60`: 请求超时时间60秒

### 3. 使用Systemd服务（推荐）

```bash
# 创建日志目录
mkdir -p /var/log/infoweb

# 复制服务文件
sudo cp infoweb.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start infoweb

# 开机自启
sudo systemctl enable infoweb

# 查看状态
sudo systemctl status infoweb

# 查看日志
sudo journalctl -u infoweb -f
```

## 方案二：使用Waitress（Windows推荐）

```bash
# 安装waitress
pip install waitress

# 启动
start-prod.bat
```

## 性能对比

| 服务器 | 适用场景 | 性能 | 稳定性 |
|--------|----------|------|--------|
| Flask开发服务器 | 开发调试 | 低 | 低 |
| Gunicorn | Linux生产 | 高 | 高 |
| Waitress | Windows生产 | 中 | 高 |
| uWSGI | 大规模生产 | 很高 | 很高 |

## 生产环境优化建议

### 1. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 关闭Flask调试模式

编辑 `modules/config.py`：

```python
FLASK_DEBUG = False
```

### 3. 配置日志轮转

```bash
# 安装logrotate（如果不存在）
sudo apt install logrotate

# 创建配置文件 /etc/logrotate.d/infoweb
/var/log/infoweb/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

## 监控服务

```bash
# 查看进程
ps aux | grep gunicorn

# 查看端口占用
netstat -tlnp | grep 5000

# 查看资源占用
top -p $(pgrep -d',' gunicorn)
```
