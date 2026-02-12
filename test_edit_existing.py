#!/usr/bin/env python3
"""
已有案件数据编辑测试脚本
对已有案件进行证据、申请人、被申请人、请求的增删改操作，并验证结果
"""

import requests
import random
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []
    
    def add(self, name, success, detail=""):
        if success:
            self.passed += 1
            status = "[OK]"
        else:
            self.failed += 1
            status = "[FAIL]"
        self.details.append((name, status, detail))
        print(f"{status} {name}")
        if detail:
            print(f"      {detail}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n总计: {total} | 通过: {self.passed} | 失败: {self.failed}")
        return self.failed == 0


def get_all_cases():
    """获取所有案件列表"""
    try:
        r = requests.get(f"{API_URL}/cases/list?page=1&page_size=100")
        result = r.json()
        if result.get('success'):
            return result['data']['list']
        return []
    except Exception as e:
        print(f"获取案件列表失败: {e}")
        return []


def get_case_detail(case_id):
    """获取案件详情"""
    try:
        r = requests.get(f"{API_URL}/cases/{case_id}")
        return r.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def save_case(data):
    """保存案件"""
    try:
        r = requests.post(f"{API_URL}/cases/save", json=data)
        return r.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def delete_case(case_id):
    """删除案件"""
    try:
        r = requests.delete(f"{API_URL}/cases/{case_id}")
        return r.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_add_applicant_to_existing_case(case, result):
    """测试: 向现有案件添加新申请人"""
    print(f"\n测试案件 {case['receipt_number']}: 添加申请人")
    
    # 获取案件详情
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("添加申请人", False, "获取详情失败")
        return
    
    data = detail['data']
    original_count = len(data['applicants'])
    
    # 添加新申请人
    new_applicant = {
        "seq_no": original_count + 1,
        "name": "新增申请人",
        "gender": "男",
        "nation": "汉族",
        "birth_date": "1990年01月",
        "address": "测试地址",
        "phone": "13800138000",
        "id_card": "110101199001011234",
        "employment_date": "2020年01月",
        "work_location": "测试公司",
        "monthly_salary": "10000元",
        "facts_reasons": "新增申请人的事实与理由",
        "requests": [{"seq_no": 1, "content": "新增请求:支付工资10000元"}]
    }
    data['applicants'].append(new_applicant)
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    # 保存
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("添加申请人", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['applicants'])
        if new_count == original_count + 1:
            result.add("添加申请人", True, f"{original_count} -> {new_count}")
        else:
            result.add("添加申请人", False, f"数量不匹配: 期望{original_count+1}, 实际{new_count}")
    else:
        result.add("添加申请人", False, "验证查询失败")


def test_remove_applicant_from_case(case, result):
    """测试: 从案件删除申请人"""
    print(f"\n测试案件 {case['receipt_number']}: 删除申请人")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("删除申请人", False, "获取详情失败")
        return
    
    data = detail['data']
    original_count = len(data['applicants'])
    
    if original_count <= 1:
        result.add("删除申请人", True, "只有1个申请人，跳过删除测试")
        return
    
    # 删除最后一个申请人
    removed_name = data['applicants'][-1]['name']
    data['applicants'].pop()
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("删除申请人", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['applicants'])
        if new_count == original_count - 1:
            result.add("删除申请人", True, f"删除'{removed_name}', {original_count} -> {new_count}")
        else:
            result.add("删除申请人", False, f"数量不匹配: 期望{original_count-1}, 实际{new_count}")
    else:
        result.add("删除申请人", False, "验证查询失败")


def test_add_evidence_to_case(case, result):
    """测试: 向案件添加新证据"""
    print(f"\n测试案件 {case['receipt_number']}: 添加证据")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("添加证据", False, "获取详情失败")
        return
    
    data = detail['data']
    original_count = len(data['evidence'])
    
    # 添加新证据
    new_evidence = {
        "seq_no": original_count + 1,
        "name": "新增证据-测试文档",
        "source": "申请人提供",
        "purpose": "证明新增的证据内容",
        "page_range": f"{original_count*2+1}-{original_count*2+2}",
        "applicant_seq_no": 1
    }
    data['evidence'].append(new_evidence)
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("添加证据", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['evidence'])
        if new_count == original_count + 1:
            result.add("添加证据", True, f"{original_count} -> {new_count}")
        else:
            result.add("添加证据", False, f"数量不匹配: 期望{original_count+1}, 实际{new_count}")
    else:
        result.add("添加证据", False, "验证查询失败")


def test_remove_evidence_from_case(case, result):
    """测试: 从案件删除证据"""
    print(f"\n测试案件 {case['receipt_number']}: 删除证据")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("删除证据", False, "获取详情失败")
        return
    
    data = detail['data']
    original_count = len(data['evidence'])
    
    if original_count <= 1:
        result.add("删除证据", True, "只有1份证据，跳过删除测试")
        return
    
    # 删除最后一份证据
    removed_name = data['evidence'][-1]['name']
    data['evidence'].pop()
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("删除证据", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['evidence'])
        if new_count == original_count - 1:
            result.add("删除证据", True, f"删除'{removed_name}', {original_count} -> {new_count}")
        else:
            result.add("删除证据", False, f"数量不匹配: 期望{original_count-1}, 实际{new_count}")
    else:
        result.add("删除证据", False, "验证查询失败")


def test_add_request_to_applicant(case, result):
    """测试: 向申请人添加新请求"""
    print(f"\n测试案件 {case['receipt_number']}: 添加仲裁请求")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("添加请求", False, "获取详情失败")
        return
    
    data = detail['data']
    if not data['applicants']:
        result.add("添加请求", False, "无申请人")
        return
    
    applicant = data['applicants'][0]
    original_count = len(applicant['requests'])
    
    # 添加新请求
    new_request = {
        "seq_no": original_count + 1,
        "content": f"新增请求{original_count+1}:支付经济补偿金{random.randint(1,10)*1000}元"
    }
    applicant['requests'].append(new_request)
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("添加请求", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['applicants'][0]['requests'])
        if new_count == original_count + 1:
            result.add("添加请求", True, f"申请人1: {original_count} -> {new_count}")
        else:
            result.add("添加请求", False, f"数量不匹配: 期望{original_count+1}, 实际{new_count}")
    else:
        result.add("添加请求", False, "验证查询失败")


def test_remove_request_from_applicant(case, result):
    """测试: 从申请人删除请求"""
    print(f"\n测试案件 {case['receipt_number']}: 删除仲裁请求")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("删除请求", False, "获取详情失败")
        return
    
    data = detail['data']
    if not data['applicants']:
        result.add("删除请求", False, "无申请人")
        return
    
    applicant = data['applicants'][0]
    original_count = len(applicant['requests'])
    
    if original_count <= 1:
        result.add("删除请求", True, "只有1个请求，跳过删除测试")
        return
    
    # 删除最后一个请求
    applicant['requests'].pop()
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("删除请求", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['applicants'][0]['requests'])
        if new_count == original_count - 1:
            result.add("删除请求", True, f"申请人1: {original_count} -> {new_count}")
        else:
            result.add("删除请求", False, f"数量不匹配: 期望{original_count-1}, 实际{new_count}")
    else:
        result.add("删除请求", False, "验证查询失败")


def test_modify_applicant_info(case, result):
    """测试: 修改申请人信息"""
    print(f"\n测试案件 {case['receipt_number']}: 修改申请人信息")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("修改申请人", False, "获取详情失败")
        return
    
    data = detail['data']
    if not data['applicants']:
        result.add("修改申请人", False, "无申请人")
        return
    
    applicant = data['applicants'][0]
    original_name = applicant['name']
    original_salary = applicant.get('monthly_salary', '')
    
    # 修改信息
    applicant['name'] = original_name + "（已修改）"
    applicant['monthly_salary'] = "99999元"
    applicant['phone'] = "13999999999"
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("修改申请人", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        modified = verify['data']['applicants'][0]
        if modified['name'] == original_name + "（已修改）" and modified['monthly_salary'] == "99999元":
            result.add("修改申请人", True, f"姓名和工资已修改")
        else:
            result.add("修改申请人", False, f"修改未生效")
    else:
        result.add("修改申请人", False, "验证查询失败")


def test_modify_respondent_info(case, result):
    """测试: 修改被申请人信息"""
    print(f"\n测试案件 {case['receipt_number']}: 修改被申请人信息")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("修改被申请人", False, "获取详情失败")
        return
    
    data = detail['data']
    if not data['respondents']:
        result.add("修改被申请人", False, "无被申请人")
        return
    
    respondent = data['respondents'][0]
    original_name = respondent['name']
    
    # 修改信息
    respondent['name'] = "修改后的公司名称"
    respondent['legal_person'] = "新法定代表人"
    respondent['phone'] = "010-99999999"
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("修改被申请人", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        modified = verify['data']['respondents'][0]
        if modified['name'] == "修改后的公司名称" and modified['legal_person'] == "新法定代表人":
            result.add("修改被申请人", True, "名称和法人已修改")
        else:
            result.add("修改被申请人", False, "修改未生效")
    else:
        result.add("修改被申请人", False, "验证查询失败")


def test_clear_all_evidence(case, result):
    """测试: 清空所有证据"""
    print(f"\n测试案件 {case['receipt_number']}: 清空所有证据")
    
    detail = get_case_detail(case['id'])
    if not detail.get('success'):
        result.add("清空证据", False, "获取详情失败")
        return
    
    data = detail['data']
    original_count = len(data['evidence'])
    
    # 清空证据
    data['evidence'] = []
    data['case_id'] = case['id']
    data['receipt_number'] = case['receipt_number']
    data['mode'] = 'update'
    
    save_result = save_case(data)
    if not save_result.get('success'):
        result.add("清空证据", False, f"保存失败: {save_result.get('error')}")
        return
    
    # 验证
    verify = get_case_detail(case['id'])
    if verify.get('success'):
        new_count = len(verify['data']['evidence'])
        if new_count == 0:
            result.add("清空证据", True, f"{original_count} -> 0")
        else:
            result.add("清空证据", False, f"未清空: 还剩{new_count}")
    else:
        result.add("清空证据", False, "验证查询失败")


def run_all_tests():
    """运行所有编辑测试"""
    print("=" * 70)
    print("已有案件编辑测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取所有案件
    cases = get_all_cases()
    if not cases:
        print("没有可用案件，请先创建案件")
        return
    
    print(f"\n找到 {len(cases)} 个案件")
    
    result = TestResult()
    
    # 对前5个案件进行多样编辑测试
    test_cases = cases[:5]
    
    for i, case in enumerate(test_cases):
        print(f"\n{'='*70}")
        print(f"案件 {i+1}/{len(test_cases)}: {case['receipt_number']}")
        print(f"当前: 申请人{case['applicant_count']}人, 被申请人{case['respondent_count']}家, 证据{case['evidence_count']}份")
        print('='*70)
        
        # 执行各种编辑操作
        test_add_applicant_to_existing_case(case, result)
        test_add_request_to_applicant(case, result)
        test_add_evidence_to_case(case, result)
        test_modify_applicant_info(case, result)
        test_modify_respondent_info(case, result)
        test_remove_request_from_applicant(case, result)
        test_remove_evidence_from_case(case, result)
        test_remove_applicant_from_case(case, result)
        
    # 对第6个案件进行极端测试
    if len(cases) >= 6:
        case = cases[5]
        print(f"\n{'='*70}")
        print(f"极端测试: 清空证据 {case['receipt_number']}")
        print('='*70)
        test_clear_all_evidence(case, result)
    
    # 汇总
    print(f"\n{'='*70}")
    print("测试总结")
    print('='*70)
    result.summary()


if __name__ == "__main__":
    # 检查服务
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print("服务未启动")
            exit(1)
    except:
        print(f"无法连接服务: {BASE_URL}")
        exit(1)
    
    run_all_tests()
