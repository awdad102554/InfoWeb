#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试庭审笔录提取脚本
测试多种不同格式的笔录数据
"""

import json
import subprocess

# 多种测试用例，涵盖不同格式
test_cases = [
    {
        "name": "标准格式-合议庭",
        "textPart1": """永安市劳动人事争议仲裁委员会
案    号：明永劳人仲案字[2025]427号
案    由：关于劳动报酬、福利待遇、经济补偿争议

开庭时间：2026年03月04日09时30分
开庭地点：一号仲裁庭""",
        "textPart2": """申请人：李上梅，男，汉族，1981年3月5日出生，身份证住址：福建省三明市大田县建设镇建设村189号。
委托代理人：范文秀，福建君来律师事务所律师。

被申请人：永安金牛水泥有限公司，统一社会信用代码: 91350481MA344GA649。
法定代表人：章旭升，总经理。
委托代理人：徐小健，单位工作人员。""",
        "textPart3": """仲：根据《中华人民共和国劳动争议调解仲裁法》第31条的规定，本案由胡海亮、黄燕黎、吴 洁（合议）审理，陈文婷担任书记员。"""
    },
    {
        "name": "独任仲裁员格式",
        "textPart1": """永州市劳动人事争议仲裁委员会
案号：永劳人仲案字〔2026〕103号
案由：关于工资争议

开庭时间：2026年3月20日上午9时
地点：永州市劳动人事争议仲裁委员会第三仲裁庭""",
        "textPart2": """申请人：赵小龙，男，汉族，1995年5月15日出生，公民身份号码：43110319950515XXXX。
委托代理人：刘律师，湖南湘南律师事务所律师。

被申请人：永州科创网络科技有限公司，统一社会信用代码：91431100MA4RXXXXXX。
法定代表人：吴志远，职务：执行董事。""",
        "textPart3": """仲：根据《中华人民共和国劳动争议调解仲裁法》第31条的规定，本案由张建军（独任）审理，陈小燕担任书记员。"""
    },
    {
        "name": "无空格案号格式",
        "textPart1": """永安市劳动人事争议仲裁委员会
案号：永劳人仲案字[2025]100号
案由：确认劳动关系争议

开庭时间：2025年12月31日14时00分
地点：一号仲裁庭""",
        "textPart2": """申请人：王大力，男，汉族，1985年1月1日出生。
被申请人：永州科技有限公司，统一社会信用代码：91431100XXXXXXXXXX。""",
        "textPart3": """仲：本案由王大伟独任审理，陈小红担任书记员。"""
    },
    {
        "name": "带中括号案号",
        "textPart1": """永安市劳动人事争议仲裁委员会
案号：永劳人仲案字[2026]15号
案由：关于工伤待遇争议

开庭时间：2026年1月15日上午9时00分""",
        "textPart2": """申请人：张三，男，汉族，1975年5月5日出生。
被申请人：永安市XX建筑公司。""",
        "textPart3": """仲：本案由李四、王五（合议）审理，赵六担任书记员。"""
    },
    {
        "name": "多个争议类型",
        "textPart1": """永安市劳动人事争议仲裁委员会
案    号：明永劳人仲案字[2025]50号
案    由：关于工资、加班费、经济补偿金争议

开庭时间：2025年10月10日上午9时30分""",
        "textPart2": """申请人：陈小明，男，汉族，1988年8月8日出生。
委托代理人：郑律师。

被申请人：永安市XX制造有限公司。
委托代理人：林经理。""",
        "textPart3": """仲：本案由周法官、吴仲裁员、郑仲裁员（合议）审理，何书记员担任书记员。"""
    },
    {
        "name": "最小化信息",
        "textPart1": """永安市劳动人事争议仲裁委员会
案号：永劳人仲案字〔2025〕1号
开庭时间：2025年1月1日""",
        "textPart2": """申请人：测试申请人。
被申请人：测试被申请人。""",
        "textPart3": """仲：本案由测试仲裁员独任审理，测试书记员担任书记员。"""
    },
    {
        "name": "繁体字地名",
        "textPart1": """開封市劳动人事争议仲裁委员会
案号：开劳人仲案字[2025]88号
案由：关于社会保险争议

开庭时间：2025年6月6日上午10时""",
        "textPart2": """申请人：刘测试，男，汉族，1990年1月1日出生。
被申请人：开封市XX有限公司。""",
        "textPart3": """仲：本案由马仲裁员、牛仲裁员、杨仲裁员（合议）审理，朱书记员担任书记员。"""
    },
    {
        "name": "textPart3为JSON格式",
        "textPart1": """永安市劳动人事争议仲裁委员会
案号：永劳人仲案字〔2025〕200号
案由：关于劳动报酬争议

开庭时间：2025年8月8日上午9时00分""",
        "textPart2": """申请人：赵测试，男，汉族，1980年1月1日出生。
被申请人：永安市XX公司。""",
        "textPart3": json.dumps({
            "开庭笔录": "仲：本案由孙仲裁员、钱仲裁员、李仲裁员（合议）审理，周书记员担任书记员。"
        })
    },
]


def run_extractor(text_part1, text_part2, text_part3):
    """调用提取脚本"""
    input_data = {
        'textPart1': text_part1,
        'textPart2': text_part2,
        'textPart3': text_part3
    }
    
    proc = subprocess.Popen(
        ['python3', 'court_record_extractor.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=json.dumps(input_data))
    
    try:
        return json.loads(stdout), stderr
    except:
        return None, stderr or stdout


def main():
    print("=" * 80)
    print("庭审笔录提取脚本 - 批量兼容性测试")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'='*80}")
        
        result, error = run_extractor(
            test_case['textPart1'],
            test_case['textPart2'],
            test_case['textPart3']
        )
        
        if result:
            success_count += 1
            print("✓ 提取成功")
            print(f"  案号: {result.get('案号', 'N/A')}")
            print(f"  委员会: {result.get('委员会', 'N/A')}")
            print(f"  案由: {result.get('案由', 'N/A')}")
            print(f"  开庭时间: {result.get('开庭时间', 'N/A')}")
            print(f"  首席仲裁员: {result.get('首席仲裁员', 'N/A')}")
            print(f"  仲裁员1: {result.get('仲裁员1', 'N/A')}")
            print(f"  仲裁员2: {result.get('仲裁员2', 'N/A')}")
            print(f"  书记员: {result.get('书记员', 'N/A')}")
        else:
            fail_count += 1
            print("✗ 提取失败")
            print(f"  错误: {error}")
    
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"总测试数: {len(test_cases)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/len(test_cases)*100:.1f}%")


if __name__ == "__main__":
    main()
