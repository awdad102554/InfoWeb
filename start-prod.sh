#!/bin/bash

# 劳动仲裁信息查询综合服务平台 - 生产环境启动脚本
# 使用Gunicorn作为WSGI服务器

export LANG=zh_CN.UTF-8

cd "$(dirname "$0")"

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 检查gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "正在安装Gunicorn..."
    pip install gunicorn
fi

# 获取CPU核心数用于设置worker数量
WORKERS=${WORKERS:-4}
PORT=${PORT:-5000}
HOST=${HOST:-0.0.0.0}

echo "========================================"
echo "劳动仲裁信息查询综合服务平台 (生产环境)"
echo "========================================"
echo "工作进程数: $WORKERS"
echo "监听地址: $HOST:$PORT"
echo "========================================"
echo ""

# 启动Gunicorn
# --bind: 绑定地址
# --workers: 工作进程数 (通常设为CPU核心数*2+1)
# --timeout: 超时时间(秒)
# --access-logfile: 访问日志
# --error-logfile: 错误日志
# --capture-output: 捕获Python输出
# --enable-stdio-inheritance: 允许子进程继承标准IO
exec gunicorn \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --timeout 60 \
    --access-logfile access.log \
    --error-logfile error.log \
    --capture-output \
    --enable-stdio-inheritance \
    --reload \
    app:app
