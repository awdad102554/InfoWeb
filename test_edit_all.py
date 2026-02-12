#!/usr/bin/env python3
"""
完整编辑测试 - 测试已有案件的各种编辑操作
"""
import requests
import json
from datetime import datetime

API_URL = 'http://localhost:5000/api'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            status = "[OK]"
        else:
            self.failed += 1
            status = "[FAIL]"
        self.results.append((name, status, detail))
        print(f"{status} {name} {detail}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n总计: {total} | 通过: {self.passed} | 失败: {self.failed}")


def get_cases():
    r = requests.get(f'{API_URL}/cases/list?page=1&page_size=10')
    return r.json()['data']['list']


def get_detail(case_id):
    r = requests.get(f'{API_URL}/cases/{case_id}')
    return r.json()['data']


def save(data):
    r = requests.post(f'{API_URL}/cases/save', json=data)
    return r.json()


def prepare_save_data(detail, case_id, receipt_number):
    """准备保存数据 - 将detail转换为API需要的格式"""
    return {
        'case_id': case_id,
        'receipt_number': receipt_number,
        'mode': 'update',
        'applicants': detail['applicants'],
        'respondents': detail['respondents'],
        'evidence': detail['evidence']
    }


def main():
    print("="*60)
    print("已有案件编辑测试")
    print("="*60)
    
    test = TestRunner()
    cases = get_cases()
    print(f"找到 {len(cases)} 个案件\n")
    
    if len(cases) < 5:
        print("案件数量不足，建议先运行 test_stress.py 创建测试数据")
        return
    
    # === 测试1: 添加证据 ===
    print("\n【测试1】添加证据")
    case = cases[0]
    detail = get_detail(case['id'])
    old_count = len(detail['evidence'])
    
    detail['evidence'].append({
        'seq_no': old_count + 1,
        'name': '新增证据-劳动合同补充',
        'source': '申请人1提供',
        'purpose': '证明补充的劳动关系',
        'page_range': '99-101',
        'applicant_seq_no': 1
    })
    
    save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
    result = save(save_data)
    
    if result.get('success'):
        new_detail = get_detail(case['id'])
        test.check("添加证据", len(new_detail['evidence']) == old_count + 1, 
                   f"{old_count} -> {len(new_detail['evidence'])}")
    else:
        test.check("添加证据", False, f"保存失败: {result.get('error')}")
    
    # === 测试2: 删除证据 ===
    print("\n【测试2】删除证据")
    case = cases[1]
    detail = get_detail(case['id'])
    old_count = len(detail['evidence'])
    
    if old_count > 0:
        detail['evidence'].pop()
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            test.check("删除证据", len(new_detail['evidence']) == old_count - 1,
                       f"{old_count} -> {len(new_detail['evidence'])}")
        else:
            test.check("删除证据", False, f"保存失败: {result.get('error')}")
    else:
        test.check("删除证据", True, "跳过: 无证据")
    
    # === 测试3: 添加申请人 ===
    print("\n【测试3】添加申请人")
    case = cases[2]
    detail = get_detail(case['id'])
    old_count = len(detail['applicants'])
    
    detail['applicants'].append({
        'seq_no': old_count + 1,
        'name': '测试添加申请人',
        'gender': '男',
        'nation': '汉族',
        'birth_date': '1985年06月',
        'address': '测试地址',
        'phone': '13800138001',
        'id_card': '110101198506151234',
        'employment_date': '2019年01月',
        'work_location': '测试公司',
        'monthly_salary': '8000元',
        'facts_reasons': '测试添加申请人的事实理由',
        'requests': [{'seq_no': 1, 'content': '请求支付工资8000元'}]
    })
    
    save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
    result = save(save_data)
    
    if result.get('success'):
        new_detail = get_detail(case['id'])
        test.check("添加申请人", len(new_detail['applicants']) == old_count + 1,
                   f"{old_count} -> {len(new_detail['applicants'])}")
    else:
        test.check("添加申请人", False, f"保存失败: {result.get('error')}")
    
    # === 测试4: 删除申请人 ===
    print("\n【测试4】删除申请人")
    case = cases[3]
    detail = get_detail(case['id'])
    old_count = len(detail['applicants'])
    
    if old_count > 1:
        detail['applicants'].pop()
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            test.check("删除申请人", len(new_detail['applicants']) == old_count - 1,
                       f"{old_count} -> {len(new_detail['applicants'])}")
        else:
            test.check("删除申请人", False, f"保存失败: {result.get('error')}")
    else:
        test.check("删除申请人", True, "跳过: 只有1个申请人")
    
    # === 测试5: 修改申请人信息 ===
    print("\n【测试5】修改申请人信息")
    case = cases[4]
    detail = get_detail(case['id'])
    
    if detail['applicants']:
        old_name = detail['applicants'][0]['name']
        detail['applicants'][0]['name'] = old_name + "(已修改)"
        detail['applicants'][0]['monthly_salary'] = "99999元"
        
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            new_name = new_detail['applicants'][0]['name']
            new_salary = new_detail['applicants'][0]['monthly_salary']
            test.check("修改申请人", new_name == old_name + "(已修改)" and new_salary == "99999元",
                       f"姓名:{new_name}, 工资:{new_salary}")
        else:
            test.check("修改申请人", False, f"保存失败: {result.get('error')}")
    else:
        test.check("修改申请人", False, "无申请人")
    
    # === 测试6: 添加仲裁请求 ===
    print("\n【测试6】添加仲裁请求")
    case = cases[0]  # 复用第一个案件
    detail = get_detail(case['id'])
    
    if detail['applicants']:
        old_count = len(detail['applicants'][0]['requests'])
        detail['applicants'][0]['requests'].append({
            'seq_no': old_count + 1,
            'content': '新增请求:支付经济补偿金50000元'
        })
        
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            new_count = len(new_detail['applicants'][0]['requests'])
            test.check("添加请求", new_count == old_count + 1,
                       f"{old_count} -> {new_count}")
        else:
            test.check("添加请求", False, f"保存失败: {result.get('error')}")
    else:
        test.check("添加请求", False, "无申请人")
    
    # === 测试7: 删除仲裁请求 ===
    print("\n【测试7】删除仲裁请求")
    case = cases[1]  # 复用第二个案件
    detail = get_detail(case['id'])
    
    if detail['applicants']:
        old_count = len(detail['applicants'][0]['requests'])
        if old_count > 1:
            detail['applicants'][0]['requests'].pop()
            
            save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
            result = save(save_data)
            
            if result.get('success'):
                new_detail = get_detail(case['id'])
                new_count = len(new_detail['applicants'][0]['requests'])
                test.check("删除请求", new_count == old_count - 1,
                           f"{old_count} -> {new_count}")
            else:
                test.check("删除请求", False, f"保存失败: {result.get('error')}")
        else:
            test.check("删除请求", True, "跳过: 只有1个请求")
    else:
        test.check("删除请求", False, "无申请人")
    
    # === 测试8: 修改被申请人信息 ===
    print("\n【测试8】修改被申请人信息")
    case = cases[2]  # 复用第三个案件
    detail = get_detail(case['id'])
    
    if detail['respondents']:
        detail['respondents'][0]['name'] = "修改后的公司名称(测试)"
        detail['respondents'][0]['legal_person'] = "新法人(测试)"
        
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            new_name = new_detail['respondents'][0]['name']
            new_person = new_detail['respondents'][0]['legal_person']
            test.check("修改被申请人", "修改后的" in new_name and "新法人" in new_person,
                       f"公司:{new_name}, 法人:{new_person}")
        else:
            test.check("修改被申请人", False, f"保存失败: {result.get('error')}")
    else:
        test.check("修改被申请人", False, "无被申请人")
    
    # === 测试9: 清空所有证据 ===
    print("\n【测试9】清空所有证据")
    case = cases[3]  # 复用第四个案件
    detail = get_detail(case['id'])
    old_count = len(detail['evidence'])
    
    detail['evidence'] = []
    save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
    result = save(save_data)
    
    if result.get('success'):
        new_detail = get_detail(case['id'])
        test.check("清空证据", len(new_detail['evidence']) == 0,
                   f"{old_count} -> 0")
    else:
        test.check("清空证据", False, f"保存失败: {result.get('error')}")
    
    # === 测试10: 修改事实与理由 ===
    print("\n【测试10】修改事实与理由")
    case = cases[4]  # 复用第五个案件
    detail = get_detail(case['id'])
    
    if detail['applicants']:
        detail['applicants'][0]['facts_reasons'] = "这是修改后的事实与理由内容，用于测试修改功能。"
        
        save_data = prepare_save_data(detail, case['id'], case['receipt_number'])
        result = save(save_data)
        
        if result.get('success'):
            new_detail = get_detail(case['id'])
            new_facts = new_detail['applicants'][0]['facts_reasons']
            test.check("修改事实理由", "修改后" in new_facts, "内容已更新")
        else:
            test.check("修改事实理由", False, f"保存失败: {result.get('error')}")
    else:
        test.check("修改事实理由", False, "无申请人")
    
    # 汇总
    print("\n" + "="*60)
    test.summary()


if __name__ == "__main__":
    try:
        r = requests.get('http://localhost:5000/api/health', timeout=5)
        if r.status_code != 200:
            print("服务未启动")
            exit(1)
    except:
        print("无法连接服务")
        exit(1)
    
    main()
