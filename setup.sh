#!/bin/bash

# 劳动仲裁信息查询综合服务平台 - 初始化脚本

echo "========================================"
echo "劳动仲裁信息查询综合服务平台 - 初始化"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "请先安装Python3: sudo apt install python3 python3-venv -y"
    exit 1
fi

# 检查python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo "正在安装 python3-venv..."
    sudo apt update
    sudo apt install python3-venv -y
fi

# 创建虚拟环境
echo ""
echo "[1/3] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "虚拟环境创建完成"
fi

# 激活虚拟环境并安装依赖
echo ""
echo "[2/3] 安装Python依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "依赖安装失败"
    exit 1
fi
echo "依赖安装完成"

# 检查配置
echo ""
echo "[3/3] 检查配置..."
python3 -c "
import sys
sys.path.insert(0, 'modules')
from config import Config
print(f'数据库: {Config.DB_HOST}:{Config.DB_PORT}')
print(f'服务端口: {Config.FLASK_PORT}')
"

echo ""
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo ""
echo "启动服务命令:"
echo "  ./start.sh"
echo ""
echo "或者手动启动:"
echo "  source venv/bin/activate"
echo "  python3 start.py"
echo ""
