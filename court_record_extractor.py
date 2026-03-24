#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
劳动仲裁庭审笔录信息提取脚本
功能：从 textPart1、textPart2、textPart3 中提取关键法律要素，并格式化为标准JSON结构

输入：textPart1（开庭信息）、textPart2（当事人信息）、textPart3（笔录内容）
输出：标准JSON结构
"""

import json
import re
import sys
from typing import Dict, Optional


def format_arbitrator_name(name: str) -> str:
    """
    格式化仲裁员姓名：2字姓名中间插入 &nbsp;
    如："吴洁" → "吴&nbsp;洁"
    """
    if not name:
        return name
    name = name.strip()
    # 如果姓名正好是2个汉字，在中间插入 &nbsp;
    if len(name) == 2 and all('\u4e00' <= char <= '\u9fff' for char in name):
        return f"{name[0]}&nbsp;{name[1]}"
    return name


def extract_committee(text: str) -> str:
    """提取委员会全称"""
    patterns = [
        r'([\u4e00-\u9fa5]+劳动人事争议仲裁委员会)',
        r'([\u4e00-\u9fa5]+劳动争议仲裁委员会)',
        r'([\u4e00-\u9fa5]+仲裁委员会)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def extract_case_no(text: str) -> str:
    """
    提取并标准化案号
    支持 "案    号：" 等带空格格式，支持 [] 或 〔〕 括号
    标准化为 "永劳人仲案字〔YYYY〕XX号"（去掉特定前缀如"明"）
    """
    patterns = [
        r'案\s*号\s*[:：]\s*([\u4e00-\u9fa5]*劳人仲案字\s*[\[〔]?\d{4}[\]〕]?\s*\d+\s*号?)',
        r'案\s*号\s*[:：]\s*([\u4e00-\u9fa5]*劳仲案字\s*[\[〔]?\d{4}[\]〕]?\s*\d+\s*号?)',
        r'([\u4e00-\u9fa5]+劳人仲案字\s*[\[〔]\d{4}[\]〕]\s*\d+号?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            case_no = match.group(1)
            case_no = re.sub(r'\s+', '', case_no)
            # 统一转换为中文括号〔〕
            case_no = case_no.replace('[', '〔').replace(']', '〕')
            # 去掉特定前缀 "明"，保留 "永劳人仲案字" 格式
            case_no = re.sub(r'^明(?=永)', '', case_no)
            return case_no
    
    return ""


def extract_case_reason(text: str) -> str:
    """
    提取案由并标准化为 "支付+争议类型"
    优先从 "关于...争议" 提取，支持多个争议类型组合
    """
    # 匹配关于...争议（支持顿号分隔的多个类型）
    about_pattern = r'关于\s*([\u4e00-\u9fa5、]+?)\s*争议'
    match = re.search(about_pattern, text)
    if match:
        reason = match.group(1).strip()
        # 处理顿号分隔的多个类型
        if '、' in reason:
            types = reason.split('、')
            if len(types) >= 2:
                reason = f"{types[0]}等"
        if 2 <= len(reason) <= 20:
            if not reason.startswith('支付'):
                return f"支付{reason}"
            return reason
    
    # 其次匹配案由字段
    case_reason_patterns = [
        r'案由\s*[:：]\s*关于?\s*([\u4e00-\u9fa5]{2,10})\s*争议?',
        r'案由\s*[:：]\s*支付?\s*([\u4e00-\u9fa5]{2,10})',
    ]
    
    for pattern in case_reason_patterns:
        match = re.search(pattern, text)
        if match:
            reason = match.group(1).strip()
            if len(reason) > 20 or len(reason) < 2:
                continue
            if reason.startswith('关于'):
                reason = reason[2:]
            if not reason.startswith('支付'):
                return f"支付{reason}"
            return reason
    
    return ""


def format_date_no_leading_zero(date_str: str) -> str:
    """
    将日期格式中的前导零去除
    2026年03月04日 -> 2026年3月4日
    """
    # 匹配年月日格式
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
    if match:
        year = match.group(1)
        month = int(match.group(2))  # 去除前导零
        day = int(match.group(3))    # 去除前导零
        return f"{year}年{month}月{day}日"
    return date_str


def extract_hearing_time(text: str) -> str:
    """
    提取开庭时间
    格式：YYYY年M月D日+时段（上午/下午），月份日期不带前导零
    """
    patterns = [
        r'开庭时间\s*[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日[^\n]*)',
        r'时间\s*[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日[^\n]*)',
        r'(\d{4}年\d{1,2}月\d{1,2}日[\s上下午\d:]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1).strip()
            time_str = re.sub(r'\s+', '', time_str)
            # 简化时间为上下午
            if re.search(r'\d+时\d+分', time_str) or re.search(r'\d+:\d+', time_str):
                hour_match = re.search(r'(\d+)[时:]', time_str)
                if hour_match:
                    hour = int(hour_match.group(1))
                    date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', time_str)
                    if date_match:
                        base_time = format_date_no_leading_zero(date_match.group(1))
                        if '下午' in time_str or '晚上' in time_str or hour >= 13:
                            return f"{base_time}下午"
                        elif '上午' in time_str or hour < 12:
                            return f"{base_time}上午"
                        else:
                            return f"{base_time}上午"
            # 处理没有时间的情况，只返回日期（去除前导零）
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', time_str)
            if date_match:
                return format_date_no_leading_zero(date_match.group(1))
            return time_str
    
    return ""


def extract_arbitrators_from_part3(text_part3: str) -> Dict[str, str]:
    """
    从textPart3中提取仲裁员和书记员信息
    
    注意：textPart3的提取逻辑与part1/part2不同：
    - part1/part2: 必须同时满足 title和save_path都包含"开庭/庭审笔录"，只取第一份
    - part3: 只要title包含"开庭/庭审笔录"，收集所有符合条件的笔录的part3
    
    支持多种格式：
    - 本案由XXX、XXX、XXX（合议）审理，XXX担任书记员
    - 本案由XXX（独任）审理，XXX担任书记员
    - 本案由XXX独任审理，XXX担任书记员
    - 本案由XXX、XXX审理，XXX担任书记员
    
    返回：
    {
        "首席仲裁员": "姓名",
        "仲裁员1": "姓名",
        "仲裁员2": "姓名",
        "书记员": "姓名"
    }
    """
    result = {
        "首席仲裁员": "",
        "仲裁员1": "",
        "仲裁员2": "",
        "书记员": ""
    }
    
    if not text_part3:
        return result
    
    # 解析textPart3（可能是JSON字符串或普通字符串）
    text_content = ""
    try:
        part3_data = json.loads(text_part3) if isinstance(text_part3, str) else text_part3
        if isinstance(part3_data, dict):
            # 合并所有笔录的内容
            text_content = "\n".join(str(v) for v in part3_data.values())
        else:
            text_content = str(part3_data)
    except:
        text_content = str(text_part3)
    
    # 匹配模式1：本案由XXX、XXX、XXX（合议/独任）审理，XXX担任书记员
    # 支持顿号、逗号分隔的多个仲裁员
    pattern1 = r'本案由\s*([\u4e00-\u9fff\s、,，]+?)(?:（(?:合议|独任)）|\s*(?:独任))?\s*审理[，,。]?\s*([\u4e00-\u9fff]{2,4})\s*担任书记员'
    match = re.search(pattern1, text_content)
    
    if match:
        arbitrators_str = match.group(1).strip()
        clerk_name = match.group(2).strip()
        
        # 清理后缀（合议/独任标记）
        arbitrators_str = arbitrators_str.replace('（合议）', '').replace('（独任）', '')
        arbitrators_str = arbitrators_str.replace('合议', '').replace('独任', '')
        
        # 分割仲裁员姓名（按顿号、逗号分隔）
        arbitrator_list = [name.strip() for name in re.split(r'[、,，]', arbitrators_str) if name.strip()]
        
        # 过滤掉可能的非人名项（如"本案由"前缀）
        arbitrator_list = [name for name in arbitrator_list if len(name) >= 2 and len(name) <= 8]
        
        # 分配角色
        if len(arbitrator_list) >= 1:
            result["首席仲裁员"] = format_arbitrator_name(arbitrator_list[0])
        if len(arbitrator_list) >= 2:
            result["仲裁员1"] = format_arbitrator_name(arbitrator_list[1])
        if len(arbitrator_list) >= 3:
            result["仲裁员2"] = format_arbitrator_name(arbitrator_list[2])
        
        result["书记员"] = format_arbitrator_name(clerk_name)
    
    return result


def extract_parties_info(text_part2: str) -> str:
    """
    从textPart2提取当事人和委托代理人信息
    格式：申请人信息\n委托代理人信息\n被申请人信息\n被申请人委托代理人信息
    """
    lines = []
    text_lines = text_part2.split('\n')
    
    applicant_section = []
    respondent_section = []
    current_section = None
    
    for line in text_lines:
        line = line.strip()
        if not line:
            continue
        
        # 跳过委托权限等冗余内容
        if any(keyword in line for keyword in ['委托权限', '特别授权', '一般代理', '权限：']):
            continue
        
        # 识别分区
        if line.startswith('申请人') and '被申请人' not in line:
            current_section = 'applicant'
            cleaned = clean_party_info(line)
            if cleaned:
                applicant_section.append(cleaned)
        elif line.startswith('被申请人'):
            current_section = 'respondent'
            cleaned = clean_party_info(line)
            if cleaned:
                respondent_section.append(cleaned)
        elif '委托代理人' in line or '法定代表人' in line:
            cleaned = clean_party_info(line)
            if cleaned:
                if current_section == 'applicant':
                    applicant_section.append(cleaned)
                elif current_section == 'respondent':
                    respondent_section.append(cleaned)
    
    # 合并结果
    lines = applicant_section + respondent_section
    
    return '\n'.join(lines)


def clean_party_info(text: str) -> str:
    """清洗当事人信息"""
    # 删除委托权限相关描述
    text = re.sub(r'[,，]\s*委托权限[：:]\s*[^\n]*', '', text)
    text = re.sub(r'[,，]\s*特别授权[^\n]*', '', text)
    text = re.sub(r'[,，]\s*一般代理[^\n]*', '', text)
    text = re.sub(r'委托权限[：:]\s*[^\n]*', '', text)
    text = re.sub(r'特别授权[^\n]*', '', text)
    text = re.sub(r'一般代理[^\n]*', '', text)
    # 删除多余空格
    text = re.sub(r' {2,}', ' ', text)
    # 删除末尾的逗号
    text = re.sub(r'[,，]\s*$', '', text)
    # 清理首尾空白
    text = text.strip()
    return text


def extract_court_record(text_part1: str, text_part2: str, text_part3: str, handle_at: str = "") -> Dict[str, str]:
    """
    主函数：从textPart1、textPart2、textPart3中提取所有信息
    
    注意：textPart1, textPart2, textPart3 是按照生成Word的条件获取的：
    - 必须同时满足 title 和 save_path 都包含"开庭笔录"或"庭审笔录"
    - part1/part2: 取第一份符合条件的笔录
    - part3: 收集所有符合条件的笔录的part3
    
    Args:
        text_part1: 开庭基本信息（地点、时间、案号、案由等）
        text_part2: 当事人信息（申请人、被申请人、代理人等）
        text_part3: 庭审笔录正文内容（包含仲裁员、书记员信息）
        handle_at: 受理时间（格式：XXXX年X月X日）
    
    Returns:
        标准JSON结构
    """
    # 合并textPart1和textPart2用于信息提取
    combined_text = f"{text_part1}\n{text_part2}"
    
    # 预处理文本
    combined_text = re.sub(r'案\s+号', '案号', combined_text)
    combined_text = re.sub(r'案\s+由', '案由', combined_text)
    
    result = {
        "委员会": extract_committee(combined_text),
        "案号": extract_case_no(combined_text),
        "案由": extract_case_reason(combined_text),
        "开庭时间": extract_hearing_time(combined_text),
        "受理时间": handle_at,  # 从API返回的handle_at格式化而来
        "当事人和委托代理人信息": extract_parties_info(text_part2),
        "首席仲裁员": "",
        "仲裁员1": "",
        "仲裁员2": "",
        "书记员": ""
    }
    
    # 从textPart3提取仲裁员和书记员信息
    arbitrators = extract_arbitrators_from_part3(text_part3)
    result["首席仲裁员"] = arbitrators["首席仲裁员"]
    result["仲裁员1"] = arbitrators["仲裁员1"]
    result["仲裁员2"] = arbitrators["仲裁员2"]
    result["书记员"] = arbitrators["书记员"]
    
    return result


def main():
    """主函数：处理输入并输出JSON结果"""
    import argparse
    
    parser = argparse.ArgumentParser(description='劳动仲裁庭审笔录信息提取')
    parser.add_argument('--part1', '-p1', help='textPart1: 开庭基本信息（地点、时间、案号、案由等）')
    parser.add_argument('--part2', '-p2', help='textPart2: 当事人信息（申请人、被申请人、代理人等）')
    parser.add_argument('--part3', '-p3', help='textPart3: 庭审笔录正文内容（包含仲裁员、书记员信息）')
    parser.add_argument('--json', '-j', help='JSON文件路径，包含textPart1、textPart2、textPart3')
    parser.add_argument('--test', '-t', action='store_true', help='运行测试示例')
    
    args = parser.parse_args()
    
    if args.test:
        run_test()
        return
    
    # 初始化变量
    text_part1 = ''
    text_part2 = ''
    text_part3 = ''
    handle_at = ''
    
    # 从JSON文件读取
    if args.json:
        try:
            with open(args.json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            text_part1 = data.get('textPart1', '')
            text_part2 = data.get('textPart2', '')
            text_part3 = data.get('textPart3', '')
            handle_at = data.get('handle_at', '')  # 受理时间
        except Exception as e:
            print(f"读取JSON文件失败: {e}", file=sys.stderr)
            sys.exit(1)
    # 从命令行参数读取
    elif args.part1 or args.part2 or args.part3:
        text_part1 = args.part1 or ''
        text_part2 = args.part2 or ''
        text_part3 = args.part3 or ''
    else:
        # 从标准输入读取JSON
        try:
            input_data = json.load(sys.stdin)
            text_part1 = input_data.get('textPart1', '')
            text_part2 = input_data.get('textPart2', '')
            text_part3 = input_data.get('textPart3', '')
            handle_at = input_data.get('handle_at', '')  # 受理时间
        except json.JSONDecodeError:
            print("错误：请提供JSON格式的输入，或使用--part1/--part2/--part3参数", file=sys.stderr)
            print("\n示例：")
            print('  echo \'{"textPart1":"...","textPart2":"...","textPart3":"..."}\' | python court_record_extractor.py')
            print('  python court_record_extractor.py -p1 "开庭信息" -p2 "当事人信息" -p3 "笔录内容"')
            print('  python court_record_extractor.py -j input.json')
            print('  python court_record_extractor.py -t')
            sys.exit(1)
    
    # 提取信息
    result = extract_court_record(text_part1, text_part2, text_part3, handle_at)
    
    # 输出JSON结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


def run_test():
    """运行测试示例"""
    text_part1 = """永安市劳动人事争议仲裁委员会
案    号：明永劳人仲案字[2025]427号
案    由：关于劳动报酬、福利待遇、经济补偿争议

开庭时间：2026年03月04日09时30分
开庭地点：一号仲裁庭

仲裁员：
书记员："""

    text_part2 = """申请人：李上梅，男，汉族，1981年3月5日出生，身份证住址：福建省三明市大田县建设镇建设村189号。公民身份号码：350425198103052950。
委托代理人：刘律师，福建君来律师事务所律师，委托权限：特别授权。

被申请人：永安金牛水泥有限公司，统一社会信用代码: 91350481MA344GA649，住所：永安市槐南镇槐南村后坑。
法定代表人：章旭升，总经理。
委托代理人：范文秀，该公司员工，委托权限：一般代理。"""

    text_part3 = """（二）告知当事人的权利和义务
仲：根据我国法律的有关规定，当事人在仲裁活动中享有如下权利：有委托代理人、申请回避的权利，有申诉、申辩、质询、质证的权利，有请求调解、自行和解、要求裁决的权利，依法向人民法院提起诉讼、申请强制执行的权利；申请人有放弃、变更、撤回仲裁请求的权利；被申请人有承认、反驳申请人仲裁请求的权利。
    当事人在仲裁活动中承担如下义务：有遵守仲裁程序和仲裁庭纪律的义务，有如实陈述案情、回答仲裁员提问的义务，有对自己提出的主张举证的义务，有尊重对方当事人及其他仲裁参加人的义务，有自觉履行发生法律效力的调解、裁决文书的义务。
仲：申请人听清楚了吗？
申：听清楚了。
仲：被申请人听清楚了吗？
被：听清楚了。 
仲：根据《中华人民共和国劳动争议调解仲裁法》第31条的规定，本案由胡海亮、黄燕黎、吴 洁（合议）审理，陈文婷担任书记员。如果当事人认为本庭组成人员与本案有利害关系，可能影响到本案的公正审理，可以申请本庭组成人员回避。申请人是否申请本庭组成人员回避？
申：不申请。
仲：被申请人是否申请本庭组成人员回避？
被：不申请。
二、仲裁庭审理
（一）现由申请人陈述请求事项及事实、理由。"""

    print("=" * 60)
    print("测试输入：")
    print("=" * 60)
    print("\n【textPart1 - 开庭信息】")
    print(text_part1)
    print("\n【textPart2 - 当事人信息】")
    print(text_part2)
    print("\n【textPart3 - 笔录内容】(包含仲裁员书记员信息)")
    print(text_part3[:500] + "...")
    
    print("\n" + "=" * 60)
    print("提取结果：")
    print("=" * 60)
    
    result = extract_court_record(text_part1, text_part2, text_part3)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
