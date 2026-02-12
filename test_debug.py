import requests
API_URL = 'http://localhost:5000/api'

# 获取第一个案件
cases = requests.get(f'{API_URL}/cases/list?page=1&page_size=1').json()['data']['list']
case = cases[0]
print(f'案件: {case["receipt_number"]}')

# 获取详情
detail = requests.get(f'{API_URL}/cases/{case["id"]}').json()['data']
print(f'原证据数: {len(detail["evidence"])}')

# 添加证据
detail['evidence'].append({'seq_no': 99, 'name': '测试证据', 'source': '测试', 'purpose': '测试', 'page_range': '1-2', 'applicant_seq_no': 1})
detail['case_id'] = case['id']
detail['mode'] = 'update'

# 保存
result = requests.post(f'{API_URL}/cases/save', json=detail).json()
print(f'保存结果: {result}')

# 重新获取
new_detail = requests.get(f'{API_URL}/cases/{case["id"]}').json()['data']
print(f'新证据数: {len(new_detail["evidence"])}')
