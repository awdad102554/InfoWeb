#!/usr/bin/env python3
import requests

API_URL = 'http://localhost:5000/api'

print("="*50)
print("快速编辑测试")
print("="*50)

# 1. 获取案件列表
r = requests.get(f'{API_URL}/cases/list?page=1&page_size=3')
cases = r.json()['data']['list']
print(f"找到 {len(cases)} 个案件")

if not cases:
    print("没有案件可测试")
    exit()

# 测试案件1: 添加证据
case = cases[0]
print(f"\n【测试1】案件 {case['receipt_number']}: 添加证据")
r = requests.get(f'{API_URL}/cases/{case["id"]}')
detail = r.json()['data']
old_evidence_count = len(detail['evidence'])
print(f"  原证据数: {old_evidence_count}")

detail['evidence'].append({
    'seq_no': old_evidence_count + 1,
    'name': '新增测试证据',
    'source': '申请人提供',
    'purpose': '测试添加证据功能',
    'page_range': '99-100',
    'applicant_seq_no': 1
})
detail['case_id'] = case['id']
detail['receipt_number'] = case['receipt_number']
detail['mode'] = 'update'

r = requests.post(f'{API_URL}/cases/save', json=detail)
if r.json()['success']:
    # 验证
    r = requests.get(f'{API_URL}/cases/{case["id"]}')
    new_count = len(r.json()['data']['evidence'])
    print(f"  新证据数: {new_count}")
    print(f"  结果: {'通过' if new_count == old_evidence_count + 1 else '失败'}")
else:
    print(f"  保存失败: {r.json().get('error')}")

# 测试案件2: 添加申请人
if len(cases) > 1:
    case = cases[1]
    print(f"\n【测试2】案件 {case['receipt_number']}: 添加申请人")
    r = requests.get(f'{API_URL}/cases/{case["id"]}')
    detail = r.json()['data']
    old_count = len(detail['applicants'])
    print(f"  原申请人数: {old_count}")
    
    detail['applicants'].append({
        'seq_no': old_count + 1,
        'name': '新增申请人',
        'gender': '男',
        'nation': '汉族',
        'birth_date': '1990年01月',
        'address': '测试地址',
        'phone': '13800138000',
        'id_card': '110101199001011234',
        'employment_date': '2020年01月',
        'work_location': '测试公司',
        'monthly_salary': '10000元',
        'facts_reasons': '新增申请人的事实理由',
        'requests': [{'seq_no': 1, 'content': '请求支付工资'}]
    })
    detail['case_id'] = case['id']
    detail['receipt_number'] = case['receipt_number']
    detail['mode'] = 'update'
    
    r = requests.post(f'{API_URL}/cases/save', json=detail)
    if r.json()['success']:
        r = requests.get(f'{API_URL}/cases/{case["id"]}')
        new_count = len(r.json()['data']['applicants'])
        print(f"  新申请人数: {new_count}")
        print(f"  结果: {'通过' if new_count == old_count + 1 else '失败'}")
    else:
        print(f"  保存失败: {r.json().get('error')}")

# 测试案件3: 删除证据
if len(cases) > 2:
    case = cases[2]
    print(f"\n【测试3】案件 {case['receipt_number']}: 删除证据")
    r = requests.get(f'{API_URL}/cases/{case["id"]}')
    detail = r.json()['data']
    old_count = len(detail['evidence'])
    print(f"  原证据数: {old_count}")
    
    if old_count > 0:
        removed = detail['evidence'].pop()
        detail['case_id'] = case['id']
        detail['receipt_number'] = case['receipt_number']
        detail['mode'] = 'update'
        
        r = requests.post(f'{API_URL}/cases/save', json=detail)
        if r.json()['success']:
            r = requests.get(f'{API_URL}/cases/{case["id"]}')
            new_count = len(r.json()['data']['evidence'])
            print(f"  新证据数: {new_count}")
            print(f"  结果: {'通过' if new_count == old_count - 1 else '失败'}")
        else:
            print(f"  保存失败: {r.json().get('error')}")
    else:
        print("  跳过: 无证据可删除")

print("\n" + "="*50)
print("测试完成")
