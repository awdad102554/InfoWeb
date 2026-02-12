@echo off
chcp 65001 >nul
title 劳动仲裁信息查询综合服务平台 (生产环境)

echo ========================================
echo 劳动仲裁信息查询综合服务平台 (生产环境)
echo ========================================
echo.

cd /d "%~dp0"

:: 检查虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: 检查waitress (Windows推荐的WSGI服务器)
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo 正在安装 waitress...
    pip install waitress
)

set PORT=5000
set HOST=0.0.0.0

echo 监听地址: %HOST%:%PORT%
echo ========================================
echo.

:: 使用waitress启动
python -c "
from waitress import serve
from app import app
import logging

logging.basicConfig(level=logging.INFO)
print('服务启动在 http://%s:%s' % ('%HOST%', '%PORT%'))
serve(app, host='%HOST%', port=%PORT%, threads=8)
"

pause
