#!/usr/bin/env python3
"""
压力测试与数据一致性验证脚本
模拟真实场景的大规模使用，验证增删改查操作的数据一致性
"""

import requests
import random
import string
import time
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# 测试统计
stats = {
    'total_operations': 0,
    'passed': 0,
    'failed': 0,
    'verify_passed': 0,
    'verify_failed': 0
}

# ========== 真实数据生成器 ==========

class DataGenerator:
    """生成真实的虚拟数据"""
    
    # 常见姓氏
    surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '吴', '周', '徐', '孙', '马', '朱', '胡', '郭', '林', '何', '高', '罗']
    # 常见名字
    names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞', '平', '刚', '桂英']
    # 民族
    nations = ['汉族', '回族', '满族', '蒙古族', '藏族', '维吾尔族', '苗族', '彝族', '壮族', '布依族']
    # 城市
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '苏州', '成都', '武汉', '西安', '重庆', '天津', '青岛', '大连', '厦门']
    # 区/县
    districts = ['朝阳区', '海淀区', '东城区', '西城区', '丰台区', '通州区', '昌平区', '大兴区', '房山区', '顺义区']
    # 街道
    streets = ['建国路', '复兴路', '人民路', '解放路', '中山路', '建设路', '文化路', '光明路', '胜利路', '和平路']
    # 公司名称
    company_prefixes = ['北京', '上海', '深圳', '杭州', '广州', '成都', '南京', '武汉', '西安']
    company_types = ['科技', '网络', '信息', '软件', '互联网', '电子商务', '文化传媒', '教育', '咨询', '贸易']
    company_suffixes = ['有限公司', '股份有限公司', '集团有限公司', '网络科技有限公司', '科技有限公司']
    # 仲裁请求模板
    request_templates = [
        "请求裁决被申请人支付拖欠的工资{amount}元（{period}）",
        "请求裁决被申请人支付违法解除劳动合同的赔偿金{amount}元",
        "请求裁决被申请人支付未签订书面劳动合同的双倍工资差额{amount}元",
        "请求裁决被申请人支付加班费{amount}元（{period}）",
        "请求裁决被申请人支付年休假工资报酬{amount}元",
        "请求裁决被申请人支付经济补偿金{amount}元（{months}个月×{monthly_salary}元）",
        "请求裁决被申请人为申请人补缴{period}的社会保险费",
        "请求裁决被申请人支付工伤医疗费{amount}元",
        "请求裁决被申请人支付停工留薪期工资{amount}元",
        "请求裁决被申请人支付一次性伤残补助金{amount}元"
    ]
    # 事实与理由模板
    facts_templates = [
        "申请人于{employment_date}入职被申请人单位，担任{position}一职。被申请人自{start_date}起无故拖欠工资，至今已累计拖欠{months}个月工资共计{total_amount}元。申请人多次催讨未果，为维护自身合法权益，特向贵委申请仲裁。",
        "申请人于{employment_date}入职，从事{position}工作。在职期间，被申请人未依法为申请人缴纳社会保险，且经常要求申请人加班但未支付加班费。申请人于{end_date}被迫离职，现依法申请仲裁。",
        "申请人于{employment_date}入职被申请人处，双方未签订书面劳动合同。申请人月工资为{monthly_salary}元。被申请人自{start_date}开始拖欠工资，严重侵害了申请人的合法权益。",
        "申请人于{employment_date}入职，担任{position}。2024年12月，被申请人以经营不善为由单方面解除劳动合同，但未支付任何经济补偿。申请人认为被申请人的解除行为违法，特申请仲裁。"
    ]
    # 证据类型
    evidence_types = [
        ('劳动合同', '证明申请人与被申请人之间存在劳动关系'),
        ('工资银行流水', '证明申请人的工资收入及被申请人拖欠工资的事实'),
        ('社保缴费记录', '证明被申请人为申请人缴纳社会保险的情况'),
        ('考勤记录', '证明申请人的实际出勤情况'),
        ('加班审批单', '证明申请人加班的事实及加班时长'),
        ('解除劳动关系通知书', '证明被申请人单方解除劳动合同的事实'),
        ('微信聊天记录', '证明申请人与被申请人负责人沟通的过程'),
        ('工作邮件', '证明申请人的工作内容及工作交接情况'),
        ('工资条', '证明申请人的工资构成'),
        ('入职登记表', '证明申请人的入职时间'),
        ('请假单', '证明申请人的请假情况'),
        ('培训记录', '证明申请人参加培训的情况'),
        ('绩效评估表', '证明申请人的工作表现'),
        ('工伤认定书', '证明申请人受伤属于工伤'),
        ('医疗费票据', '证明申请人支出的医疗费用')
    ]
    # 岗位
    positions = ['软件工程师', '产品经理', '销售经理', '行政主管', '财务专员', '人力资源专员', '市场专员', '客服专员', '设计师', '运营专员', '技术员', '仓库管理员', '司机', '厨师', '保安']
    
    @classmethod
    def generate_name(cls):
        """生成姓名"""
        return random.choice(cls.surnames) + random.choice(cls.names)
    
    @classmethod
    def generate_id_card(cls):
        """生成身份证号"""
        area_codes = ['110101', '310101', '440106', '330106', '320106', '510107', '420106', '610113']
        area = random.choice(area_codes)
        year = random.randint(1970, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        seq = ''.join(random.choices(string.digits, k=3))
        # 计算校验码（简化版）
        return f"{area}{year}{month:02d}{day:02d}{seq}X"
    
    @classmethod
    def generate_phone(cls):
        """生成手机号"""
        prefixes = ['138', '139', '137', '136', '135', '150', '151', '152', '157', '158', '159', '186', '187', '188', '189']
        return random.choice(prefixes) + ''.join(random.choices(string.digits, k=8))
    
    @classmethod
    def generate_address(cls):
        """生成地址"""
        city = random.choice(cls.cities)
        district = random.choice(cls.districts)
        street = random.choice(cls.streets)
        num = random.randint(1, 999)
        building = random.randint(1, 20)
        room = random.randint(101, 2500)
        return f"{city}市{district}{street}{num}号{building}号楼{room}室"
    
    @classmethod
    def generate_company_name(cls):
        """生成公司名称"""
        prefix = random.choice(cls.company_prefixes)
        ctype = random.choice(cls.company_types)
        suffix = random.choice(cls.company_suffixes)
        return f"{prefix}{ctype}{suffix}"
    
    @classmethod
    def generate_employment_date(cls):
        """生成入职日期"""
        year = random.randint(2018, 2023)
        month = random.randint(1, 12)
        return f"{year}年{month:02d}月"
    
    @classmethod
    def generate_salary(cls):
        """生成工资"""
        return random.choice(range(4000, 25000, 500))
    
    @classmethod
    def generate_request(cls, monthly_salary, months):
        """生成仲裁请求"""
        template = random.choice(cls.request_templates)
        amount = monthly_salary * months
        period = f"2024年{random.randint(1,12)}月至2024年{random.randint(1,12)}月"
        return template.format(
            amount=amount,
            period=period,
            months=months,
            monthly_salary=monthly_salary
        )
    
    @classmethod
    def generate_facts(cls, employment_date, monthly_salary, position):
        """生成事实与理由"""
        template = random.choice(cls.facts_templates)
        start_year = 2024
        start_month = random.randint(6, 11)
        months = random.randint(1, 6)
        total_amount = monthly_salary * months
        return template.format(
            employment_date=employment_date,
            position=position,
            start_date=f"{start_year}年{start_month}月",
            end_date="2024年12月",
            months=months,
            total_amount=total_amount,
            monthly_salary=f"{monthly_salary}元"
        )


# ========== 测试操作 ==========

class CaseOperator:
    """案件操作类"""
    
    def __init__(self):
        self.created_cases = []  # 记录创建的案件
    
    def create_case(self):
        """创建案件"""
        # 生成随机数据
        receipt_number = f"LA{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        # 1-3个申请人
        applicants = []
        applicant_count = random.randint(1, 3)
        for i in range(applicant_count):
            name = DataGenerator.generate_name()
            gender = random.choice(['男', '女'])
            monthly_salary = DataGenerator.generate_salary()
            position = random.choice(DataGenerator.positions)
            employment_date = DataGenerator.generate_employment_date()
            requests_count = random.randint(1, 3)
            
            applicant = {
                "seq_no": i + 1,
                "name": name,
                "gender": gender,
                "nation": random.choice(DataGenerator.nations),
                "birth_date": f"{random.randint(1970, 1995)}年{random.randint(1,12):02d}月",
                "address": DataGenerator.generate_address(),
                "phone": DataGenerator.generate_phone(),
                "id_card": DataGenerator.generate_id_card(),
                "employment_date": employment_date,
                "work_location": DataGenerator.generate_company_name(),
                "monthly_salary": f"{monthly_salary}元",
                "facts_reasons": DataGenerator.generate_facts(employment_date, monthly_salary, position),
                "requests": [
                    {"seq_no": j + 1, "content": DataGenerator.generate_request(monthly_salary, random.randint(1, 6))}
                    for j in range(requests_count)
                ]
            }
            applicants.append(applicant)
        
        # 1-2个被申请人
        respondents = []
        respondent_count = random.randint(1, 2)
        for i in range(respondent_count):
            respondent = {
                "seq_no": i + 1,
                "name": DataGenerator.generate_company_name(),
                "legal_person": DataGenerator.generate_name(),
                "position": random.choice(['总经理', '法定代表人', '负责人', '经理']),
                "address": DataGenerator.generate_address(),
                "phone": DataGenerator.generate_phone(),
                "unified_code": f"91{''.join(random.choices(string.digits, k=14))}"
            }
            respondents.append(respondent)
        
        # 2-10份证据
        evidence = []
        evidence_count = random.randint(2, 10)
        selected_evidence = random.sample(DataGenerator.evidence_types, min(evidence_count, len(DataGenerator.evidence_types)))
        for i, (evi_name, evi_purpose) in enumerate(selected_evidence):
            applicant_seq = random.randint(1, applicant_count) if applicant_count > 0 else 1
            evidence.append({
                "seq_no": i + 1,
                "name": evi_name,
                "source": f"申请人{applicant_seq}提供",
                "purpose": evi_purpose,
                "page_range": f"{i*3+1}-{i*3+random.randint(2,5)}",
                "applicant_seq_no": applicant_seq
            })
        
        data = {
            "receipt_number": receipt_number,
            "mode": "create",
            "applicants": applicants,
            "respondents": respondents,
            "evidence": evidence
        }
        
        # 发送请求
        try:
            r = requests.post(f"{API_URL}/cases/save", json=data, timeout=10)
            result = r.json()
            if result.get('success'):
                case_info = {
                    'case_id': result['case_id'],
                    'receipt_number': receipt_number,
                    'data': data
                }
                self.created_cases.append(case_info)
                return True, case_info
            return False, result.get('error')
        except Exception as e:
            return False, str(e)
    
    def query_case(self, receipt_number):
        """查询案件"""
        try:
            r = requests.get(f"{API_URL}/cases/query?receipt_number={receipt_number}", timeout=10)
            return r.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_case(self, case_info):
        """更新案件"""
        case_id = case_info['case_id']
        data = case_info['data'].copy()
        data['case_id'] = case_id
        data['mode'] = 'update'
        
        # 随机修改一些数据
        if data['applicants']:
            data['applicants'][0]['name'] = DataGenerator.generate_name() + "（已修改）"
            # 添加一个新请求
            if data['applicants'][0]['requests']:
                monthly_salary = 8000
                new_request = {
                    "seq_no": len(data['applicants'][0]['requests']) + 1,
                    "content": DataGenerator.generate_request(monthly_salary, random.randint(1, 3))
                }
                data['applicants'][0]['requests'].append(new_request)
        
        # 添加一份新证据
        if data['evidence']:
            evi_name, evi_purpose = random.choice(DataGenerator.evidence_types)
            new_evidence = {
                "seq_no": len(data['evidence']) + 1,
                "name": evi_name + "（补充）",
                "source": "申请人提供",
                "purpose": evi_purpose,
                "page_range": f"{len(data['evidence'])*3+1}-{len(data['evidence'])*3+3}",
                "applicant_seq_no": 1
            }
            data['evidence'].append(new_evidence)
        
        try:
            r = requests.post(f"{API_URL}/cases/save", json=data, timeout=10)
            return r.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_case(self, case_id):
        """删除案件"""
        try:
            r = requests.delete(f"{API_URL}/cases/{case_id}", timeout=10)
            return r.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_case_data(self, case_info, query_result):
        """验证案件数据一致性"""
        if not query_result.get('success'):
            return False, "查询失败"
        
        data = query_result.get('data', {})
        original = case_info['data']
        
        errors = []
        
        # 验证申请人数量
        if len(data.get('applicants', [])) != len(original['applicants']):
            errors.append(f"申请人数量不匹配: 期望{len(original['applicants'])}, 实际{len(data.get('applicants', []))}")
        
        # 验证被申请人数量
        if len(data.get('respondents', [])) != len(original['respondents']):
            errors.append(f"被申请人数量不匹配")
        
        # 验证证据数量
        if len(data.get('evidence', [])) != len(original['evidence']):
            errors.append(f"证据数量不匹配: 期望{len(original['evidence'])}, 实际{len(data.get('evidence', []))}")
        
        # 验证申请人姓名
        for i, app in enumerate(original['applicants']):
            if i < len(data.get('applicants', [])):
                if data['applicants'][i]['name'] != app['name']:
                    errors.append(f"申请人{i+1}姓名不匹配")
        
        # 验证收件编号
        if data.get('case', {}).get('receipt_number') != original['receipt_number']:
            errors.append("收件编号不匹配")
        
        if errors:
            return False, "; ".join(errors)
        return True, "数据一致"


# ========== 主测试流程 ==========

def run_stress_test():
    """运行压力测试"""
    print("=" * 70)
    print("压力测试与数据一致性验证")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    operator = CaseOperator()
    
    # 阶段1: 批量创建案件
    print("\n【阶段1】批量创建案件")
    create_count = 20
    for i in range(create_count):
        success, result = operator.create_case()
        stats['total_operations'] += 1
        if success:
            stats['passed'] += 1
            print(f"  [{i+1}/{create_count}] 创建成功: {result['receipt_number']} "
                  f"(申请人{len(result['data']['applicants'])} 证据{len(result['data']['evidence'])})")
        else:
            stats['failed'] += 1
            print(f"  [{i+1}/{create_count}] 创建失败: {result}")
        time.sleep(0.1)
    
    print(f"\n创建完成: 成功{stats['passed']}, 失败{stats['failed']}")
    
    # 阶段2: 查询验证
    print("\n【阶段2】查询验证数据一致性")
    for i, case_info in enumerate(operator.created_cases):
        result = operator.query_case(case_info['receipt_number'])
        stats['total_operations'] += 1
        
        is_valid, msg = operator.verify_case_data(case_info, result)
        if is_valid:
            stats['verify_passed'] += 1
            print(f"  [{i+1}] {case_info['receipt_number']}: 验证通过")
        else:
            stats['verify_failed'] += 1
            print(f"  [{i+1}] {case_info['receipt_number']}: 验证失败 - {msg}")
    
    print(f"\n验证完成: 通过{stats['verify_passed']}, 失败{stats['verify_failed']}")
    
    # 阶段3: 更新案件
    print("\n【阶段3】更新案件")
    update_cases = random.sample(operator.created_cases, min(10, len(operator.created_cases)))
    for i, case_info in enumerate(update_cases):
        result = operator.update_case(case_info)
        stats['total_operations'] += 1
        
        if result.get('success'):
            # 验证更新后数据
            query_result = operator.query_case(case_info['receipt_number'])
            if query_result.get('success'):
                # 检查是否添加了新证据
                new_evidence_count = len(query_result['data']['evidence'])
                old_evidence_count = len(case_info['data']['evidence'])
                print(f"  [{i+1}] {case_info['receipt_number']}: 更新成功 "
                      f"(证据 {old_evidence_count} -> {new_evidence_count})")
            else:
                print(f"  [{i+1}] {case_info['receipt_number']}: 更新后查询失败")
        else:
            print(f"  [{i+1}] {case_info['receipt_number']}: 更新失败 - {result.get('error')}")
    
    # 阶段4: 删除部分案件
    print("\n【阶段4】删除案件")
    delete_cases = random.sample(operator.created_cases, min(5, len(operator.created_cases)))
    for i, case_info in enumerate(delete_cases):
        result = operator.delete_case(case_info['case_id'])
        stats['total_operations'] += 1
        
        if result.get('success'):
            # 验证已删除
            query_result = operator.query_case(case_info['receipt_number'])
            if not query_result.get('success'):
                print(f"  [{i+1}] {case_info['receipt_number']}: 删除成功且无法查询")
            else:
                print(f"  [{i+1}] {case_info['receipt_number']}: 删除成功但还能查询（异常）")
        else:
            print(f"  [{i+1}] {case_info['receipt_number']}: 删除失败 - {result.get('error')}")
    
    # 阶段5: 并发测试
    print("\n【阶段5】并发查询测试")
    def concurrent_query(case_info):
        return operator.query_case(case_info['receipt_number'])
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(concurrent_query, case) for case in operator.created_cases[:10]]
        concurrent_results = [future.result() for future in as_completed(futures)]
    
    success_count = sum(1 for r in concurrent_results if r.get('success'))
    print(f"  并发查询: 成功{success_count}/{len(concurrent_results)}")
    
    # 最终统计
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"总操作数: {stats['total_operations']}")
    print(f"创建成功: {stats['passed']}")
    print(f"创建失败: {stats['failed']}")
    print(f"数据验证通过: {stats['verify_passed']}")
    print(f"数据验证失败: {stats['verify_failed']}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if stats['verify_failed'] == 0 and stats['failed'] == 0:
        print("\n[OK] 所有测试通过，数据一致性良好！")
    else:
        print(f"\n[WARN] 存在{stats['failed'] + stats['verify_failed']}个问题需要关注")


if __name__ == "__main__":
    # 检查服务
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print("服务未启动")
            exit(1)
    except:
        print(f"无法连接服务: {BASE_URL}")
        print("请先运行: python start.py")
        exit(1)
    
    run_stress_test()
