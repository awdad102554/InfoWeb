#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取案件信息JSON字符串
用于作为info参数传递给生成Word的Dify Workflow

用法:
  python3 get_case_info.py <案件ID>
  python3 get_case_info.py 203220
  
  或从标准输入读取API响应:
  curl -s "http://127.0.0.1:5000/api/handle/detail?id=203220" | python3 get_case_info.py
"""

import json
import sys
import re

# 导入提取函数
sys.path.insert(0, '/vol2/1000/python-project/InfoWeb')
from court_record_extractor import extract_court_record


def format_handle_at(handle_at: str) -> str:
    """将 handle_at 格式化为 XXXX年X月X日"""
    if not handle_at:
        return ""
    match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', str(handle_at))
    if match:
        year = match.group(1)
        month = int(match.group(2))
        day = int(match.group(3))
        return f"{year}年{month}月{day}日"
    return handle_at


def extract_from_api_response(api_data: dict):
    """从API返回数据中提取textPart1, textPart2, textPart3"""
    
    # 处理嵌套的data结构
    data = api_data.get('data', {})
    
    if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
        inner_data = data['data']
        if 'writing_json' in inner_data or 'case_no' in inner_data:
            case_detail = inner_data
        else:
            case_detail = data
    elif isinstance(data, list) and len(data) > 0:
        case_detail = data[0]
    elif isinstance(data, dict):
        case_detail = data
    else:
        case_detail = {}
    
    writing_json = case_detail.get('writing_json', [])
    
    text_part1 = ""
    text_part2 = ""
    all_records_part3 = {}
    
    for item in writing_json:
        title = item.get('title', '')
        save_path = item.get('save_path', '')
        
        if '开庭笔录' in title or '庭审笔录' in title:
            json_str = item.get('json', '{}')
            try:
                record_json = json.loads(json_str) if isinstance(json_str, str) else json_str
                
                if '开庭笔录' in save_path or '庭审笔录' in save_path:
                    if not text_part1:
                        text_part1 = record_json.get('part1', '') or ''
                    if not text_part2:
                        text_part2 = record_json.get('part2', '') or ''
                
                part3_content = record_json.get('part3', '') or ''
                if part3_content:
                    all_records_part3[title] = part3_content
            except:
                pass
    
    text_part3 = json.dumps(all_records_part3, ensure_ascii=False) if all_records_part3 else ''
    
    # 获取并格式化受理时间
    handle_at_raw = case_detail.get('handle_at', '')
    handle_at_formatted = format_handle_at(handle_at_raw)
    
    return {
        'textPart1': text_part1,
        'textPart2': text_part2,
        'textPart3': text_part3,
        'handle_at': handle_at_formatted
    }


def main():
    """主函数"""
    
    # 读取输入
    if len(sys.argv) > 1:
        # 从命令行参数获取案件ID，需要调用API
        case_id = sys.argv[1]
        print(f"请使用: curl -s 'http://127.0.0.1:5000/api/handle/detail?id={case_id}' | python3 {sys.argv[0]}", file=sys.stderr)
        sys.exit(1)
    else:
        # 从标准输入读取API响应
        try:
            stdin_data = sys.stdin.read()
            if not stdin_data.strip():
                print("错误: 标准输入为空", file=sys.stderr)
                sys.exit(1)
            api_data = json.loads(stdin_data)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    # 提取信息
    extracted = extract_from_api_response(api_data)
    
    # 检查是否有笔录数据
    if not extracted['textPart1'] and not extracted['textPart2']:
        # 返回空结果的JSON
        result = {
            "委员会": "",
            "案号": "",
            "案由": "",
            "开庭时间": "",
            "受理时间": extracted['handle_at'],
            "当事人和委托代理人信息": "",
            "首席仲裁员": "",
            "仲裁员1": "",
            "仲裁员2": "",
            "书记员": ""
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
    
    # 提取所有字段
    result = extract_court_record(
        extracted['textPart1'],
        extracted['textPart2'],
        extracted['textPart3'],
        extracted['handle_at']
    )
    
    # 输出纯JSON字符串（作为info参数）
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
