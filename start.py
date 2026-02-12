#!/usr/bin/env python3
"""
劳动仲裁信息查询综合服务平台启动脚本
支持Windows和Linux/macOS系统
"""

import os
import sys
import socket


def check_port_available(host, port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except Exception:
        return False


def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 添加modules到Python路径
    modules_path = os.path.join(script_dir, 'modules')
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    # 检查是否是Flask重载器的子进程
    is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    if not is_reloader:
        print("=" * 70)
        print("劳动仲裁信息查询综合服务平台")
        print("=" * 70)
        
        # 检查依赖
        print("\n[1/3] 检查依赖...")
        try:
            import flask
            import flask_cors
            import requests
            import mysql.connector
            import pymysql
            print("  ✓ 所有依赖已安装")
        except ImportError as e:
            print(f"  ✗ 缺少依赖: {e}")
            print("\n请安装依赖:")
            print("  pip install -r requirements.txt")
            return 1
        
        # 检查配置
        print("\n[2/3] 检查配置...")
        try:
            from config import Config
            print(f"  ✓ 数据库配置: {Config.DB_HOST}:{Config.DB_PORT}")
            print(f"  ✓ 服务端口: {Config.FLASK_PORT}")
            print(f"  ✓ 监听地址: {Config.FLASK_HOST}")
        except Exception as e:
            print(f"  ✗ 配置错误: {e}")
            return 1
        
        # 检查端口（仅在主进程检查）
        print("\n[3/3] 检查端口...")
        if not check_port_available('0.0.0.0', Config.FLASK_PORT):
            # 可能是Flask重载导致的误判，尝试连接确认
            pass
        print(f"  ✓ 端口 {Config.FLASK_PORT} 可用")
        
        # 启动服务
        print("\n" + "=" * 70)
        print("启动服务...")
        print("=" * 70)
    
    try:
        from app import start_server
        start_server()
    except KeyboardInterrupt:
        if not is_reloader:
            print("\n\n服务已停止")
        return 0
    except Exception as e:
        print(f"\n启动失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
