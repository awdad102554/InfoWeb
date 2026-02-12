#!/usr/bin/env python3
"""
全面测试脚本 - 覆盖各种边界情况和异常场景
"""

import requests
import random
import string
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# 测试统计
test_results = []


def log_test(name, success, detail=""):
    """记录测试结果"""
    status = "[OK]" if success else "[FAIL]"
    test_results.append((name, success, detail))
    print(f"{status} {name}")
    if detail:
        print(f"    {detail}")


def generate_id_card():
    """生成虚拟身份证号码"""
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


# ========== 测试用例 ==========

def test_01_empty_receipt_number():
    """测试1: 空收件编号"""
    print("\n测试1: 空收件编号")
    data = {
        "receipt_number": "",
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "测试", "requests": [{"seq_no": 1, "content": "测试"}]}],
        "respondents": [],
        "evidence": []
    }
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if not result.get('success') and '收件编号不能为空' in result.get('error', ''):
            log_test("空收件编号拦截", True)
        else:
            log_test("空收件编号拦截", False, f"未正确拦截: {result}")
    except Exception as e:
        log_test("空收件编号拦截", False, str(e))


def test_02_special_chars_in_receipt():
    """测试2: 特殊字符收件编号"""
    print("\n测试2: 特殊字符收件编号")
    special_chars = [
        "2026<SCRIPT>",
        "2026'; DROP TABLE cases; --",
        "2026测试中文",
        "2026!@#$%^&*()",
        "   2026   "
    ]
    
    for char in special_chars:
        data = {
            "receipt_number": char,
            "mode": "create",
            "applicants": [{"seq_no": 1, "name": "测试", "requests": [{"seq_no": 1, "content": "测试"}]}],
            "respondents": [],
            "evidence": []
        }
        try:
            r = requests.post(f"{API_URL}/cases/save", json=data)
            result = r.json()
            if result.get('success'):
                # 保存成功，需要清理
                case_id = result.get('case_id')
                requests.delete(f"{API_URL}/cases/{case_id}")
                log_test(f"特殊字符处理: {char[:20]}...", True, "已保存并清理")
            else:
                log_test(f"特殊字符处理: {char[:20]}...", False, result.get('error'))
        except Exception as e:
            log_test(f"特殊字符处理: {char[:20]}...", False, str(e))


def test_03_many_applicants():
    """测试3: 大量申请人"""
    print("\n测试3: 大量申请人(10人)")
    applicants = []
    for i in range(10):
        applicants.append({
            "seq_no": i + 1,
            "name": f"申请人{i+1}",
            "gender": "男" if i % 2 == 0 else "女",
            "nation": "汉族",
            "birth_date": f"{1980+i}年{i+1:02d}月",
            "address": f"地址{i+1}",
            "phone": generate_phone(),
            "id_card": generate_id_card(),
            "employment_date": "2020年01月",
            "work_location": "测试公司",
            "monthly_salary": f"{5000+i*1000}元",
            "facts_reasons": f"事实与理由{i+1}",
            "requests": [{"seq_no": 1, "content": f"请求{i+1}"}]
        })
    
    data = {
        "receipt_number": f"MANY{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": applicants,
        "respondents": [{"seq_no": 1, "name": "被申请人", "requests": []}],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if result.get('success'):
            # 查询验证
            r2 = requests.get(f"{API_URL}/cases/query?receipt_number={data['receipt_number']}")
            result2 = r2.json()
            if result2.get('success') and len(result2['data']['applicants']) == 10:
                log_test("10个申请人", True)
            else:
                log_test("10个申请人", False, "查询数据不匹配")
            # 清理
            requests.delete(f"{API_URL}/cases/{result['case_id']}")
        else:
            log_test("10个申请人", False, result.get('error'))
    except Exception as e:
        log_test("10个申请人", False, str(e))


def test_04_many_evidence():
    """测试4: 大量证据"""
    print("\n测试4: 大量证据(20份)")
    evidence = []
    for i in range(20):
        evidence.append({
            "seq_no": i + 1,
            "name": f"证据{i+1}",
            "source": f"申请人{i%2+1}提供",
            "purpose": f"证明目的{i+1}",
            "page_range": f"{i*2+1}-{i*2+2}",
            "applicant_seq_no": (i % 2) + 1
        })
    
    data = {
        "receipt_number": f"EVID{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [
            {"seq_no": 1, "name": "张三", "gender": "男", "requests": [{"seq_no": 1, "content": "请求1"}]},
            {"seq_no": 2, "name": "李四", "gender": "女", "requests": [{"seq_no": 1, "content": "请求2"}]}
        ],
        "respondents": [{"seq_no": 1, "name": "公司", "requests": []}],
        "evidence": evidence
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if result.get('success'):
            log_test("20份证据", True)
            requests.delete(f"{API_URL}/cases/{result['case_id']}")
        else:
            log_test("20份证据", False, result.get('error'))
    except Exception as e:
        log_test("20份证据", False, str(e))


def test_05_no_applicant():
    """测试5: 无申请人"""
    print("\n测试5: 无申请人")
    data = {
        "receipt_number": f"NOAPP{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [],
        "respondents": [{"seq_no": 1, "name": "公司", "requests": []}],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        log_test("无申请人", not result.get('success'), 
                 "正确拦截" if not result.get('success') else "应拒绝空申请人")
    except Exception as e:
        log_test("无申请人", False, str(e))


def test_06_no_evidence():
    """测试6: 无证据"""
    print("\n测试6: 无证据")
    data = {
        "receipt_number": f"NOEVI{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "张三", "requests": [{"seq_no": 1, "content": "请求"}]}],
        "respondents": [{"seq_no": 1, "name": "公司", "requests": []}],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if result.get('success'):
            log_test("无证据保存", True, "允许无证据案件")
            requests.delete(f"{API_URL}/cases/{result['case_id']}")
        else:
            log_test("无证据保存", False, result.get('error'))
    except Exception as e:
        log_test("无证据保存", False, str(e))


def test_07_long_text_fields():
    """测试7: 超长文本字段"""
    print("\n测试7: 超长文本字段")
    long_text = "A" * 5000  # 5000字符
    
    data = {
        "receipt_number": f"LONG{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [{
            "seq_no": 1,
            "name": "张三",
            "gender": "男",
            "facts_reasons": long_text,
            "requests": [{"seq_no": 1, "content": long_text[:100]}]
        }],
        "respondents": [{"seq_no": 1, "name": "公司" * 100}],
        "evidence": [{"seq_no": 1, "name": "证据" * 100, "purpose": long_text}]
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if result.get('success'):
            log_test("超长文本", True, "已保存")
            requests.delete(f"{API_URL}/cases/{result['case_id']}")
        else:
            log_test("超长文本", False, result.get('error'))
    except Exception as e:
        log_test("超长文本", False, str(e))


def test_08_evidence_without_applicant():
    """测试8: 证据关联不存在的申请人"""
    print("\n测试8: 证据关联不存在的申请人序号")
    data = {
        "receipt_number": f"EVIAPP{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "张三", "requests": [{"seq_no": 1, "content": "请求"}]}],
        "respondents": [{"seq_no": 1, "name": "公司"}],
        "evidence": [
            {"seq_no": 1, "name": "证据1", "applicant_seq_no": 1},  # 正常
            {"seq_no": 2, "name": "证据2", "applicant_seq_no": 99}  # 不存在的申请人
        ]
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        log_test("证据关联不存在申请人", not result.get('success'),
                 "正确拦截" if not result.get('success') else "应拒绝")
    except Exception as e:
        log_test("证据关联不存在申请人", False, str(e))


def test_09_create_update_consistency():
    """测试9: 创建-查询-更新-查询一致性"""
    print("\n测试9: 数据一致性检查")
    receipt = f"CONS{datetime.now().strftime('%H%M%S')}"
    
    # 创建
    data = {
        "receipt_number": receipt,
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "原始名", "gender": "男", "requests": [{"seq_no": 1, "content": "请求1"}]}],
        "respondents": [{"seq_no": 1, "name": "公司A"}],
        "evidence": [{"seq_no": 1, "name": "证据A"}]
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        if not result.get('success'):
            log_test("数据一致性", False, "创建失败")
            return
        
        case_id = result['case_id']
        
        # 查询1
        r = requests.get(f"{API_URL}/cases/{case_id}")
        data1 = r.json()['data']
        
        # 更新
        data['case_id'] = case_id
        data['mode'] = 'update'
        data['applicants'][0]['name'] = "修改后名"
        data['applicants'].append({"seq_no": 2, "name": "新增申请人", "requests": [{"seq_no": 1, "content": "请求2"}]})
        data['evidence'].append({"seq_no": 2, "name": "证据B"})
        
        r = requests.post(f"{API_URL}/cases/save", json=data)
        if not r.json().get('success'):
            log_test("数据一致性", False, "更新失败")
            return
        
        # 查询2
        r = requests.get(f"{API_URL}/cases/{case_id}")
        data2 = r.json()['data']
        
        # 验证
        checks = [
            (data2['applicants'][0]['name'] == "修改后名", "申请人姓名更新"),
            (len(data2['applicants']) == 2, "申请人数量"),
            (len(data2['evidence']) == 2, "证据数量"),
            (data2['respondents'][0]['name'] == "公司A", "被申请人未变")
        ]
        
        all_pass = all(c[0] for c in checks)
        detail = ", ".join([f"{'OK' if c[0] else 'FAIL'}:{c[1]}" for c in checks])
        log_test("数据一致性", all_pass, detail)
        
        # 清理
        requests.delete(f"{API_URL}/cases/{case_id}")
        
    except Exception as e:
        log_test("数据一致性", False, str(e))


def test_10_update_nonexistent_case():
    """测试10: 更新不存在的案件"""
    print("\n测试10: 更新不存在的案件")
    data = {
        "receipt_number": "TEST99999",
        "case_id": 99999,
        "mode": "update",
        "applicants": [{"seq_no": 1, "name": "测试", "requests": [{"seq_no": 1, "content": "请求"}]}],
        "respondents": [],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        result = r.json()
        log_test("更新不存在案件", not result.get('success') and r.status_code == 404,
                 "正确返回404" if r.status_code == 404 else f"状态码: {r.status_code}")
    except Exception as e:
        log_test("更新不存在案件", False, str(e))


def test_11_delete_already_deleted():
    """测试11: 重复删除同一案件"""
    print("\n测试11: 重复删除同一案件")
    
    # 先创建一个
    data = {
        "receipt_number": f"DEL2X{datetime.now().strftime('%H%M%S')}",
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "测试", "requests": [{"seq_no": 1, "content": "请求"}]}],
        "respondents": [],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        case_id = r.json()['case_id']
        
        # 第一次删除
        r1 = requests.delete(f"{API_URL}/cases/{case_id}")
        success1 = r1.json().get('success')
        
        # 第二次删除
        r2 = requests.delete(f"{API_URL}/cases/{case_id}")
        success2 = r2.json().get('success')
        
        log_test("重复删除", success1 and not success2,
                 f"第一次:{'成功' if success1 else '失败'}, 第二次:{'应失败' if not success2 else '不应成功'}")
    except Exception as e:
        log_test("重复删除", False, str(e))


def test_12_change_receipt_number():
    """测试12: 编辑时修改收件编号"""
    print("\n测试12: 编辑时修改收件编号")
    
    receipt1 = f"R1{datetime.now().strftime('%H%M%S')}"
    receipt2 = f"R2{datetime.now().strftime('%H%M%S')}"
    
    # 创建案件1
    data = {
        "receipt_number": receipt1,
        "mode": "create",
        "applicants": [{"seq_no": 1, "name": "测试", "requests": [{"seq_no": 1, "content": "请求"}]}],
        "respondents": [],
        "evidence": []
    }
    
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        case_id = r.json()['case_id']
        
        # 修改为新的编号
        data['case_id'] = case_id
        data['mode'] = 'update'
        data['receipt_number'] = receipt2
        
        r = requests.post(f"{API_URL}/cases/save", json=data)
        if r.json().get('success'):
            # 验证新编号能查到
            r2 = requests.get(f"{API_URL}/cases/query?receipt_number={receipt2}")
            success = r2.json().get('success')
            
            # 验证旧编号查不到
            r3 = requests.get(f"{API_URL}/cases/query?receipt_number={receipt1}")
            not_found = not r3.json().get('success')
            
            log_test("修改收件编号", success and not_found, 
                     f"新编号可查询:{success}, 旧编号查不到:{not_found}")
        else:
            log_test("修改收件编号", False, r.json().get('error'))
    except Exception as e:
        log_test("修改收件编号", False, str(e))


def test_13_sql_injection():
    """测试13: SQL注入防护"""
    print("\n测试13: SQL注入防护")
    
    malicious_inputs = [
        "'; DROP TABLE cases; --",
        "1 OR 1=1",
        "' UNION SELECT * FROM cases --",
        "'; DELETE FROM cases WHERE 1=1; --"
    ]
    
    for payload in malicious_inputs:
        data = {
            "receipt_number": f"SQL{datetime.now().strftime('%H%M%S')}",
            "mode": "create",
            "applicants": [{"seq_no": 1, "name": payload, "requests": [{"seq_no": 1, "content": payload}]}],
            "respondents": [{"seq_no": 1, "name": payload}],
            "evidence": [{"seq_no": 1, "name": payload, "purpose": payload}]
        }
        
        try:
            r = requests.post(f"{API_URL}/cases/save", json=data)
            if r.json().get('success'):
                # 如果能保存，验证数据未被破坏
                case_id = r.json()['case_id']
                r2 = requests.get(f"{API_URL}/cases/{case_id}")
                result = r2.json()
                if result.get('success'):
                    log_test(f"SQL注入防护: {payload[:30]}...", True, "数据安全保存")
                    requests.delete(f"{API_URL}/cases/{case_id}")
                else:
                    log_test(f"SQL注入防护: {payload[:30]}...", False, "查询失败")
            else:
                log_test(f"SQL注入防护: {payload[:30]}...", False, "保存被拒绝")
        except Exception as e:
            log_test(f"SQL注入防护: {payload[:30]}...", False, str(e))


def print_summary():
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in test_results if success)
    failed = len(test_results) - passed
    
    for name, success, detail in test_results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
        if detail:
            print(f"      {detail}")
    
    print(f"\n总计: {len(test_results)}项 | 通过: {passed}项 | 失败: {failed}项")
    
    if failed == 0:
        print("\n所有测试通过!")
    else:
        print(f"\n有{failed}项测试未通过")


if __name__ == "__main__":
    print("=" * 60)
    print("全面测试 - 劳动仲裁案件管理系统")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print("服务状态异常")
            exit(1)
    except:
        print(f"无法连接服务: {BASE_URL}")
        exit(1)
    
    print("服务连接正常，开始测试...\n")
    
    # 运行所有测试
    test_01_empty_receipt_number()
    test_02_special_chars_in_receipt()
    test_03_many_applicants()
    test_04_many_evidence()
    test_05_no_applicant()
    test_06_no_evidence()
    test_07_long_text_fields()
    test_08_evidence_without_applicant()
    test_09_create_update_consistency()
    test_10_update_nonexistent_case()
    test_11_delete_already_deleted()
    test_12_change_receipt_number()
    test_13_sql_injection()
    
    print_summary()
