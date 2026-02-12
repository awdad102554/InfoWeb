#!/bin/bash

# 劳动仲裁信息查询综合服务平台启动脚本

# 设置字符集
export LANG=zh_CN.UTF-8

echo "========================================"
echo "劳动仲裁信息查询综合服务平台"
echo "========================================"
echo ""

# 获取脚本所在目录
cd "$(dirname "$0")"

# 检查是否存在虚拟环境
if [ -d "venv" ]; then
    echo "检测到虚拟环境，正在激活..."
    source venv/bin/activate
else
    echo "未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败，请确保已安装 python3-venv"
        echo "安装命令: sudo apt install python3-venv -y"
        exit 1
    fi
    source venv/bin/activate
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请确保Python3已安装"
    exit 1
fi

# 启动服务
echo "正在启动服务..."
echo ""
python3 start.py
