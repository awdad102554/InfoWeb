@echo off
chcp 65001 >nul
title 劳动仲裁信息查询综合服务平台

echo ========================================
echo 劳动仲裁信息查询综合服务平台
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

:: 获取脚本所在目录
cd /d "%~dp0"

:: 启动服务
echo 正在启动服务...
echo.
python start.py

pause
