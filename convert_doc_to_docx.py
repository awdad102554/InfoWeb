#!/usr/bin/env python3
"""
批量将 .doc 转换为 .docx 格式
使用 LibreOffice 命令行工具
"""
import os
import subprocess
import sys
from pathlib import Path

def convert_doc_to_docx(input_path, output_dir=None):
    """
    将单个 .doc 文件转换为 .docx
    """
    if not os.path.exists(input_path):
        print(f"✗ 文件不存在: {input_path}")
        return False
    
    if not input_path.endswith('.doc'):
        print(f"✗ 不是 .doc 文件: {input_path}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建命令
    # --headless: 无界面模式
    # --convert-to docx: 转换为 docx 格式
    # --outdir: 输出目录
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'docx',
        '--outdir', output_dir,
        input_path
    ]
    
    try:
        print(f"转换中: {os.path.basename(input_path)} ...", end=' ')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        if result.returncode == 0:
            # 检查输出文件是否存在
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, base_name + '.docx')
            
            if os.path.exists(output_path):
                print(f"✓ 成功 -> {os.path.basename(output_path)}")
                return True
            else:
                print(f"✗ 输出文件未生成")
                return False
        else:
            print(f"✗ 失败: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ 超时")
        return False
    except FileNotFoundError:
        print(f"✗ 未找到 LibreOffice，请安装: apt install libreoffice")
        return False
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def batch_convert_directory(base_path, delete_original=False):
    """
    批量转换目录中的所有 .doc 文件
    """
    doc_files = []
    
    # 递归查找所有 .doc 文件
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.doc') and not file.startswith('~'):
                doc_files.append(os.path.join(root, file))
    
    if not doc_files:
        print(f"未找到 .doc 文件: {base_path}")
        return
    
    print(f"找到 {len(doc_files)} 个 .doc 文件")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for doc_file in doc_files:
        if convert_doc_to_docx(doc_file):
            success_count += 1
            # 可选：删除原文件
            if delete_original:
                try:
                    os.remove(doc_file)
                    print(f"  已删除原文件: {os.path.basename(doc_file)}")
                except Exception as e:
                    print(f"  删除原文件失败: {e}")
        else:
            fail_count += 1
    
    print("=" * 60)
    print(f"转换完成: 成功 {success_count} 个, 失败 {fail_count} 个")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='批量转换 .doc 为 .docx')
    parser.add_argument('path', nargs='?', default='文件生成', 
                        help='要转换的目录或文件路径 (默认: 文件生成)')
    parser.add_argument('--delete', '-d', action='store_true',
                        help='转换成功后删除原 .doc 文件')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        # 转换单个文件
        convert_doc_to_docx(args.path)
    else:
        # 批量转换目录
        batch_convert_directory(args.path, delete_original=args.delete)
