#!/usr/bin/env python3
"""
自动化测试脚本 - 虚拟数据测试案件管理功能
使用 requests 直接调用 API，无需浏览器驱动
"""

import requests
import random
import string
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"


def generate_receipt_number():
    """生成收件编号"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"{date_str}{random_num}"


def generate_id_card():
    """生成虚拟身份证号码"""
    # 地区码 + 出生日期 + 顺序码 + 校验码
    area_code = random.choice(['350102', '350103', '350104', '350105', '350111'])
    year = random.randint(1960, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    birth = f"{year}{month:02d}{day:02d}"
    seq = ''.join(random.choices(string.digits, k=3))
    return f"{area_code}{birth}{seq}X"


def generate_phone():
    """生成虚拟手机号"""
    prefixes = ['138', '139', '137', '136', '135', '150', '151', '152', '157', '158', '159']
    return random.choice(prefixes) + ''.join(random.choices(string.digits, k=8))


def create_test_case_data():
    """创建测试案件数据"""
    
    # 虚拟申请人数据
    applicants = [
        {
            "seq_no": 1,
            "name": "张三",
            "gender": "男",
            "nation": "汉族",
            "birth_date": "1985年06月",
            "address": "福建省福州市鼓楼区五四路123号",
            "phone": generate_phone(),
            "id_card": generate_id_card(),
            "employment_date": "2020年03月",
            "work_location": "福建科技有限公司",
            "monthly_salary": "8000元",
            "facts_reasons": "申请人于2020年3月入职被申请人单位，从事软件开发工作。被申请人自2024年10月起无故拖欠工资，至今已累计拖欠3个月工资共计24000元。申请人多次催讨未果，为维护自身合法权益，特向贵委申请仲裁。",
            "requests": [
                {"seq_no": 1, "content": "请求裁决被申请人支付拖欠的工资24000元（2024年10月至12月，每月8000元）"},
                {"seq_no": 2, "content": "请求裁决被申请人支付经济补偿金32000元（4个月×8000元）"},
                {"seq_no": 3, "content": "请求裁决被申请人为申请人补缴2024年1月至12月的社会保险"}
            ]
        },
        {
            "seq_no": 2,
            "name": "李四",
            "gender": "女",
            "nation": "汉族",
            "birth_date": "1988年03月",
            "address": "福建省福州市台江区工业路456号",
            "phone": generate_phone(),
            "id_card": generate_id_card(),
            "employment_date": "2019年08月",
            "work_location": "福建科技有限公司",
            "monthly_salary": "6500元",
            "facts_reasons": "申请人于2019年8月入职，担任行政主管一职。被申请人同样拖欠申请人2024年10月至12月工资共计19500元。申请人与张三系同事关系，遭遇相同。",
            "requests": [
                {"seq_no": 1, "content": "请求裁决被申请人支付拖欠的工资19500元（2024年10月至12月，每月6500元）"},
                {"seq_no": 2, "content": "请求裁决被申请人支付经济补偿金26000元（4个月×6500元）"}
            ]
        }
    ]
    
    # 虚拟被申请人数据
    respondents = [
        {
            "seq_no": 1,
            "name": "福建科技有限公司",
            "legal_person": "王五",
            "position": "总经理",
            "address": "福建省福州市仓山区金山大道88号科技大厦10层",
            "phone": "0591-12345678",
            "unified_code": "91350100MA1234567X"
        }
    ]
    
    # 虚拟证据数据
    evidence = [
        {
            "seq_no": 1,
            "name": "劳动合同",
            "source": "申请人1(张三)提供",
            "purpose": "证明申请人与被申请人之间存在劳动关系，约定了工作岗位和工资标准",
            "page_range": "1-5",
            "applicant_seq_no": 1
        },
        {
            "seq_no": 2,
            "name": "工资银行流水",
            "source": "申请人1(张三)提供",
            "purpose": "证明被申请人拖欠工资的事实及具体金额",
            "page_range": "6-10",
            "applicant_seq_no": 1
        },
        {
            "seq_no": 3,
            "name": "社保缴费记录",
            "source": "申请人1(张三)提供",
            "purpose": "证明被申请人未依法为申请人缴纳社会保险",
            "page_range": "11-12",
            "applicant_seq_no": 1
        },
        {
            "seq_no": 4,
            "name": "微信催款记录",
            "source": "申请人2(李四)提供",
            "purpose": "证明申请人多次向被申请人催讨工资的事实",
            "page_range": "13-15",
            "applicant_seq_no": 2
        }
    ]
    
    return {
        "receipt_number": generate_receipt_number(),
        "applicants": applicants,
        "respondents": respondents,
        "evidence": evidence
    }


def test_save_case():
    """测试保存案件"""
    print("=" * 60)
    print("测试1: 保存案件")
    print("=" * 60)
    
    case_data = create_test_case_data()
    print(f"收件编号: {case_data['receipt_number']}")
    print(f"申请人数量: {len(case_data['applicants'])}")
    print(f"被申请人数量: {len(case_data['respondents'])}")
    print(f"证据数量: {len(case_data['evidence'])}")
    
    try:
        response = requests.post(
            f"{API_URL}/cases/save",
            json=case_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 保存成功! 案件ID: {result.get('case_id')}")
            return case_data['receipt_number'], result.get('case_id')
        else:
            print(f"[FAIL] 保存失败: {result.get('error')}")
            return None, None
    except Exception as e:
        print(f"[FAIL] 请求异常: {str(e)}")
        return None, None


def test_query_case(receipt_number):
    """测试查询案件"""
    print("\n" + "=" * 60)
    print("测试2: 查询案件")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_URL}/cases/query?receipt_number={receipt_number}"
        )
        result = response.json()
        
        if result.get('success'):
            data = result.get('data', {})
            case = data.get('case', {})
            applicants = data.get('applicants', [])
            respondents = data.get('respondents', [])
            evidence = data.get('evidence', [])
            
            print(f"[OK] 查询成功!")
            print(f"  案件ID: {case.get('id')}")
            print(f"  收件编号: {case.get('receipt_number')}")
            print(f"  申请人: {len(applicants)}人")
            for app in applicants:
                print(f"    - {app.get('name')} ({app.get('id_card')})")
            print(f"  被申请人: {len(respondents)}家")
            for resp in respondents:
                print(f"    - {resp.get('name')}")
            print(f"  证据: {len(evidence)}份")
            return True
        else:
            print(f"[FAIL] 查询失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"[FAIL] 请求异常: {str(e)}")
        return False


def test_list_cases():
    """测试获取案件列表"""
    print("\n" + "=" * 60)
    print("测试3: 获取案件列表")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/cases/list?page=1&page_size=10")
        result = response.json()
        
        if result.get('success'):
            data = result.get('data', {})
            cases = data.get('list', [])
            total = data.get('total', 0)
            
            print(f"[OK] 获取列表成功!")
            print(f"  总案件数: {total}")
            print(f"  本页显示: {len(cases)}条")
            
            for case in cases[:5]:  # 只显示前5条
                print(f"  - ID:{case.get('id')} [{case.get('receipt_number')}] "
                      f"申请人:{case.get('applicant_count')} "
                      f"证据:{case.get('evidence_count')}")
            return True
        else:
            print(f"[FAIL] 获取列表失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"[FAIL] 请求异常: {str(e)}")
        return False


def test_update_case(receipt_number):
    """测试更新案件"""
    print("\n" + "=" * 60)
    print("测试4: 更新案件")
    print("=" * 60)
    
    # 先查询获取案件ID
    try:
        response = requests.get(
            f"{API_URL}/cases/query?receipt_number={receipt_number}"
        )
        result = response.json()
        
        if not result.get('success'):
            print(f"[FAIL] 查询案件失败: {result.get('error')}")
            return False
        
        # 创建修改后的数据
        case_data = create_test_case_data()
        case_data['receipt_number'] = receipt_number  # 保持原编号
        
        # 修改申请人信息
        case_data['applicants'][0]['name'] = "张三（已修改）"
        case_data['applicants'][0]['monthly_salary'] = "10000元"
        
        # 添加一个新的证据
        case_data['evidence'].append({
            "seq_no": 5,
            "name": "补充证据-考勤记录",
            "source": "申请人1提供",
            "purpose": "证明申请人实际出勤情况",
            "page_range": "16-20",
            "applicant_seq_no": 1
        })
        
        print(f"更新案件: {receipt_number}")
        print(f"修改申请人姓名为: {case_data['applicants'][0]['name']}")
        print(f"新增证据: 考勤记录")
        
        response = requests.post(
            f"{API_URL}/cases/save",
            json=case_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 更新成功!")
            return True
        else:
            print(f"[FAIL] 更新失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"[FAIL] 请求异常: {str(e)}")
        return False


def test_delete_case(receipt_number):
    """测试删除案件"""
    print("\n" + "=" * 60)
    print("测试5: 删除案件（软删除）")
    print("=" * 60)
    
    try:
        # 先查询获取案件ID
        response = requests.get(
            f"{API_URL}/cases/query?receipt_number={receipt_number}"
        )
        result = response.json()
        
        if not result.get('success'):
            print(f"[FAIL] 查询案件失败: {result.get('error')}")
            return False
        
        case_id = result['data']['case']['id']
        
        response = requests.delete(f"{API_URL}/cases/{case_id}")
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 删除成功! 案件ID: {case_id}")
            
            # 验证删除后查询不到
            response = requests.get(
                f"{API_URL}/cases/query?receipt_number={receipt_number}"
            )
            result = response.json()
            
            if not result.get('success'):
                print(f"[OK] 验证成功: 已删除案件无法查询到")
                return True
            else:
                print(f"[WARN] 警告: 删除后仍能查询到案件")
                return False
        else:
            print(f"[FAIL] 删除失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"[FAIL] 请求异常: {str(e)}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始自动化测试 - 劳动仲裁案件管理系统")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {BASE_URL}")
    
    results = []
    
    # 测试1: 保存案件
    receipt_number, case_id = test_save_case()
    if receipt_number:
        results.append(("保存案件", True))
        
        # 测试2: 查询案件
        results.append(("查询案件", test_query_case(receipt_number)))
        
        # 测试3: 获取案件列表
        results.append(("获取列表", test_list_cases()))
        
        # 测试4: 更新案件
        results.append(("更新案件", test_update_case(receipt_number)))
        
        # 再次查询验证更新
        results.append(("查询更新后", test_query_case(receipt_number)))
        
        # 测试5: 删除案件
        results.append(("删除案件", test_delete_case(receipt_number)))
    else:
        results.append(("保存案件", False))
        print("\n[FAIL] 保存案件失败，跳过后续测试")
    
    # 最终统计
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {len(results)}项 | 通过: {passed}项 | 失败: {failed}项")
    
    if failed == 0:
        print("\n[PASS] 所有测试全部通过!")
    else:
        print(f"\n[WARN] 有{failed}项测试未通过，请检查")


if __name__ == "__main__":
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("[OK] 服务连接正常")
            run_all_tests()
        else:
            print(f"[WARN] 服务状态异常: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] 无法连接到服务: {BASE_URL}")
        print("请确保服务已启动: python start.py")
    except Exception as e:
        print(f"[FAIL] 连接测试失败: {str(e)}")
