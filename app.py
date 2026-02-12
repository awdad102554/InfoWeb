#!/usr/bin/env python3
"""
劳动仲裁信息查询综合服务平台
整合功能：
1. 前端页面服务（劳动仲裁申请书填写、案件查询）
2. 内部API服务（企业信息查询、身份证信息查询）
3. 数据库API服务（案件数据增删改查）

部署在 10.99.144.x 网段
"""

import sys
import os

# 添加modules目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging
from datetime import datetime
import pymysql
import json

# 导入原有模块
from config import Config
from login_manager import get_login_manager
from company_query import get_company_query
from id_card_query import get_id_card_query_manager
from database import get_db_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # 启用CORS支持

# 初始化管理器
login_manager = get_login_manager()
company_query = get_company_query()
db_manager = get_db_manager()

# ============================================
# 页面路由
# ============================================

@app.route('/')
def index():
    """首页 - 劳动仲裁申请书在线填写"""
    return render_template('index.html')


@app.route('/query')
def query_page():
    """案件查询页面"""
    return render_template('query_test.html')


@app.route('/cases')
def cases_manage_page():
    """案件管理页面"""
    return render_template('cases_manage.html')


# ============================================
# 内部API服务（原Info项目）
# ============================================

@app.route('/api/status', methods=['GET'])
def api_status():
    """API状态检查"""
    return jsonify({
        'code': 200,
        'message': 'API服务运行正常',
        'service': '劳动仲裁信息查询综合服务平台',
        'timestamp': datetime.now().isoformat(),
        'status': {
            'flask': 'running',
            'login_service': 'connected' if login_manager else 'disconnected',
            'query_service': 'connected' if company_query else 'disconnected',
            'database': 'connected' if db_manager.connection else 'disconnected'
        }
    })


@app.route('/api/login/status', methods=['GET'])
def login_status():
    """获取登录状态"""
    status = login_manager.get_login_status()
    return jsonify({
        'code': 200,
        'message': '登录状态查询成功',
        'data': status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/login', methods=['POST'])
def manual_login():
    """手动登录接口"""
    try:
        data = request.get_json()
        force = data.get('force', False) if data else False
        
        login_result = login_manager.login(force=force)
        
        return jsonify({
            'code': login_result['code'],
            'message': login_result['message'],
            'data': {
                'authKey': login_result.get('authKey'),
                'sessionId': login_result.get('sessionId'),
                'expiry_time': login_result.get('expiry_time')
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"手动登录接口错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/company/query', methods=['POST'])
def query_company():
    """查询企业信息接口"""
    try:
        data = request.get_json()
        
        if not data or 'company_name' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少参数: company_name',
                'data': None,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        company_name = data['company_name']
        exact_match = data.get('exact_match', True)
        
        logger.info(f"API查询请求: {company_name}, 精确匹配: {exact_match}")
        
        query_result = company_query.query_company_info(company_name, exact_match)
        
        response_data = {
            'code': query_result['code'],
            'message': query_result['message'],
            'query_info': {
                'company_name': company_name,
                'exact_match': exact_match,
                'total_count': query_result.get('total_count', 0),
                'matched_count': query_result.get('matched_count', 0),
                'source': query_result.get('source', 'unknown')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        if query_result.get('data'):
            format_data = data.get('format', True)
            if format_data:
                formatted_data = []
                for item in query_result['data']:
                    formatted_item = company_query.format_company_info(item)
                    if formatted_item:
                        formatted_data.append(formatted_item)
                response_data['data'] = formatted_data
            else:
                response_data['data'] = query_result['data']
        else:
            response_data['data'] = None
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"查询企业信息接口错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/idcard/query', methods=['POST'])
def query_id_card():
    """查询身份证信息接口"""
    try:
        data = request.get_json()
        
        if not data or 'AAC147' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少参数: AAC147 (身份证号码)',
                'data': None,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        id_card_number = data['AAC147']
        
        logger.info(f"身份证查询请求: {id_card_number}")
        
        id_card_query_manager = get_id_card_query_manager()
        query_result = id_card_query_manager.query_id_card(id_card_number)
        
        response_data = {
            'code': query_result['code'],
            'message': query_result['message'],
            'data': query_result.get('data'),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"查询身份证信息接口错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/db/status', methods=['GET'])
def db_status():
    """获取数据库状态"""
    try:
        db_connected = db_manager.connection is not None
        login_records = db_manager.get_all_logins()
        expired_deleted = db_manager.delete_expired_logins()
        
        status_info = {
            'database_connected': db_connected,
            'total_login_records': len(login_records),
            'expired_records_deleted': expired_deleted,
            'login_records': login_records,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'code': 200,
            'message': '数据库状态查询成功',
            'data': status_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"数据库状态查询错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'数据库状态查询错误: {str(e)}',
            'data': None,
            'timestamp': datetime.now().isoformat()
        }), 500


# ============================================
# 数据库API服务（原db_api_server.py）
# ============================================

def get_labor_db_connection():
    """获取劳动仲裁数据库连接"""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4'
    )


@app.route('/api/cases/save', methods=['POST'])
def save_case():
    """保存完整案件数据（新建或更新）"""
    data = request.json
    receipt_number = data.get('receipt_number')
    applicants = data.get('applicants', [])
    respondents = data.get('respondents', [])
    evidence = data.get('evidence', [])
    case_id = data.get('case_id')  # 编辑模式时传入
    mode = data.get('mode', 'create')  # 'create' 或 'update'
    
    if not receipt_number:
        return jsonify({'success': False, 'error': '收件编号不能为空'}), 400
    
    if not applicants or len(applicants) == 0:
        return jsonify({'success': False, 'error': '至少需要一个申请人'}), 400
    
    conn = get_labor_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 根据模式处理案件主表
        if mode == 'create':
            # 新建模式：检查收件编号是否已存在
            cursor.execute(
                "SELECT id FROM cases WHERE receipt_number = %s AND status = 1",
                (receipt_number,)
            )
            existing_case = cursor.fetchone()
            
            if existing_case:
                return jsonify({
                    'success': False, 
                    'error': f'收件编号 "{receipt_number}" 已存在，无法创建',
                    'code': 'DUPLICATE_RECEIPT_NUMBER'
                }), 409
            
            # 插入新案件
            cursor.execute(
                "INSERT INTO cases (receipt_number) VALUES (%s)",
                (receipt_number,)
            )
            case_id = cursor.lastrowid
            
        else:  # update 模式
            # 编辑模式：必须提供 case_id
            if not case_id:
                return jsonify({'success': False, 'error': '编辑模式必须提供案件ID'}), 400
            
            # 验证案件存在且状态正常
            cursor.execute(
                "SELECT id, receipt_number FROM cases WHERE id = %s AND status = 1",
                (case_id,)
            )
            existing_case = cursor.fetchone()
            
            if not existing_case:
                return jsonify({'success': False, 'error': '案件不存在或已被删除'}), 404
            
            # 如果修改了收件编号，检查新编号是否与其他案件冲突
            existing_receipt = existing_case[1]
            if receipt_number != existing_receipt:
                cursor.execute(
                    "SELECT id FROM cases WHERE receipt_number = %s AND status = 1 AND id != %s",
                    (receipt_number, case_id)
                )
                if cursor.fetchone():
                    return jsonify({
                        'success': False, 
                        'error': f'收件编号 "{receipt_number}" 已被其他案件使用',
                        'code': 'DUPLICATE_RECEIPT_NUMBER'
                    }), 409
            
            # 更新案件时间
            cursor.execute(
                "UPDATE cases SET receipt_number = %s, update_time = NOW() WHERE id = %s",
                (receipt_number, case_id)
            )
            
            # 删除旧的关联数据，重新插入
            cursor.execute("DELETE FROM arbitration_requests WHERE case_id = %s", (case_id,))
            cursor.execute("DELETE FROM evidence WHERE case_id = %s", (case_id,))
            cursor.execute("DELETE FROM respondents WHERE case_id = %s", (case_id,))
            cursor.execute("DELETE FROM applicants WHERE case_id = %s", (case_id,))
        
        # 2. 插入申请人及其仲裁请求
        # 建立 seq_no -> applicant_id 映射，用于证据关联
        applicant_seq_to_id = {}
        for applicant in applicants:
            cursor.execute("""
                INSERT INTO applicants (
                    case_id, seq_no, name, gender, nation, birth_date,
                    address, phone, id_card, employment_date, work_location,
                    monthly_salary, facts_reasons
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                case_id, applicant.get('seq_no'), applicant.get('name'),
                applicant.get('gender'), applicant.get('nation'), applicant.get('birth_date'),
                applicant.get('address'), applicant.get('phone'), applicant.get('id_card'),
                applicant.get('employment_date'), applicant.get('work_location'),
                applicant.get('monthly_salary'), applicant.get('facts_reasons')
            ))
            applicant_id = cursor.lastrowid
            # 保存 seq_no 到 applicant_id 的映射
            applicant_seq_to_id[applicant.get('seq_no')] = applicant_id
            
            # 插入该申请人的仲裁请求
            for req in applicant.get('requests', []):
                cursor.execute("""
                    INSERT INTO arbitration_requests (applicant_id, case_id, seq_no, content)
                    VALUES (%s, %s, %s, %s)
                """, (applicant_id, case_id, req.get('seq_no'), req.get('content')))
        
        # 3. 插入被申请人
        for respondent in respondents:
            cursor.execute("""
                INSERT INTO respondents (
                    case_id, seq_no, name, legal_person, position,
                    address, phone, unified_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                case_id, respondent.get('seq_no'), respondent.get('name'),
                respondent.get('legal_person'), respondent.get('position'),
                respondent.get('address'), respondent.get('phone'), respondent.get('unified_code')
            ))
        
        # 4. 插入证据
        for evi in evidence:
            page_range = evi.get('page_range', '')
            page_start = ''
            page_end = ''
            if page_range and '-' in page_range:
                parts = page_range.split('-')
                page_start = parts[0]
                page_end = parts[1] if len(parts) > 1 else ''
            
            # 前端传来的是 applicant_seq_no，需要转换为真正的 applicant_id
            evi_applicant_seq = evi.get('applicant_seq_no')
            evi_applicant_id = applicant_seq_to_id.get(evi_applicant_seq) if evi_applicant_seq else None
            
            # 验证申请人存在性
            if evi_applicant_seq and evi_applicant_id is None:
                raise ValueError(f"证据 '{evi.get('name')}' 关联的申请人序号 {evi_applicant_seq} 不存在")
            
            cursor.execute("""
                INSERT INTO evidence (
                    case_id, applicant_id, seq_no, name, source, purpose, page_start, page_end, page_range
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                case_id, evi_applicant_id, evi.get('seq_no'), evi.get('name'), 
                evi.get('source'), evi.get('purpose'), page_start, page_end, page_range
            ))
        
        conn.commit()
        return jsonify({'success': True, 'case_id': case_id})
        
    except Exception as e:
        conn.rollback()
        logger.error(f"保存案件失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def get_case_detail_by_id(case_id):
    """根据案件ID获取完整详情（内部函数）"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询案件基本信息
        cursor.execute(
            "SELECT * FROM cases WHERE id = %s AND status = 1",
            (case_id,)
        )
        case = cursor.fetchone()
        
        if not case:
            return None
        
        # 查询申请人
        cursor.execute(
            "SELECT * FROM applicants WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        applicants = cursor.fetchall()
        
        # 查询每个申请人的仲裁请求
        for applicant in applicants:
            cursor.execute(
                "SELECT seq_no, content FROM arbitration_requests WHERE applicant_id = %s ORDER BY seq_no",
                (applicant['id'],)
            )
            applicant['requests'] = cursor.fetchall()
        
        # 查询被申请人
        cursor.execute(
            "SELECT * FROM respondents WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        respondents = cursor.fetchall()
        
        # 查询证据，并转换 applicant_id 为 applicant_seq_no
        cursor.execute(
            """SELECT e.*, a.seq_no as applicant_seq_no 
               FROM evidence e 
               LEFT JOIN applicants a ON e.applicant_id = a.id 
               WHERE e.case_id = %s 
               ORDER BY e.seq_no""",
            (case_id,)
        )
        evidence = cursor.fetchall()
        # 处理证据数据，将 applicant_id 替换为 applicant_seq_no
        for evi in evidence:
            evi['applicant_seq_no'] = evi.get('applicant_seq_no')  # 可能为None
        
        return {
            'case': case,
            'applicants': applicants,
            'respondents': respondents,
            'evidence': evidence
        }
        
    except Exception as e:
        logger.error(f"获取案件详情失败: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cases/query', methods=['GET'])
def query_case():
    """根据收件编号查询案件"""
    receipt_number = request.args.get('receipt_number')
    
    if not receipt_number:
        return jsonify({'success': False, 'error': '收件编号不能为空'}), 400
    
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询案件完整信息（关联查询）
        cursor.execute(
            "SELECT * FROM cases WHERE receipt_number = %s AND status = 1",
            (receipt_number,)
        )
        case = cursor.fetchone()
        
        if not case:
            return jsonify({'success': False, 'error': '案件不存在'}), 404
        
        case_id = case['id']
        
        # 查询申请人
        cursor.execute(
            "SELECT * FROM applicants WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        applicants = cursor.fetchall()
        
        # 查询每个申请人的仲裁请求
        for applicant in applicants:
            cursor.execute(
                "SELECT seq_no, content FROM arbitration_requests WHERE applicant_id = %s ORDER BY seq_no",
                (applicant['id'],)
            )
            applicant['requests'] = cursor.fetchall()
        
        # 查询被申请人
        cursor.execute(
            "SELECT * FROM respondents WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        respondents = cursor.fetchall()
        
        # 查询证据
        cursor.execute(
            "SELECT * FROM evidence WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        evidence = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'case': case,
                'applicants': applicants,
                'respondents': respondents,
                'evidence': evidence
            }
        })
        
    except Exception as e:
        logger.error(f"查询案件失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/cases/<int:case_id>', methods=['GET'])
def get_case_by_id(case_id):
    """根据案件ID查询案件详情（用于编辑）"""
    data = get_case_detail_by_id(case_id)
    
    if not data:
        return jsonify({'success': False, 'error': '案件不存在或已被删除'}), 404
    
    return jsonify({'success': True, 'data': data})


@app.route('/api/cases/list', methods=['GET'])
def list_cases():
    """获取案件列表"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询案件列表（带统计信息）
        cursor.execute("""
            SELECT 
                c.id, c.receipt_number, c.create_time, c.update_time,
                COUNT(DISTINCT a.id) AS applicant_count,
                COUNT(DISTINCT r.id) AS respondent_count,
                COUNT(DISTINCT e.id) AS evidence_count,
                GROUP_CONCAT(DISTINCT a.name ORDER BY a.seq_no) AS applicant_names
            FROM cases c
            LEFT JOIN applicants a ON c.id = a.case_id
            LEFT JOIN respondents r ON c.id = r.case_id
            LEFT JOIN evidence e ON c.id = e.case_id
            WHERE c.status = 1
            GROUP BY c.id
            ORDER BY c.create_time DESC
            LIMIT %s OFFSET %s
        """, (page_size, offset))
        cases = cursor.fetchall()
        
        # 查询总数
        cursor.execute("SELECT COUNT(*) as total FROM cases WHERE status = 1")
        total = cursor.fetchone()['total']
        
        return jsonify({
            'success': True,
            'data': {
                'list': cases,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
        
    except Exception as e:
        logger.error(f"获取案件列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cases/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    """删除案件（软删除）"""
    conn = get_labor_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先检查案件是否存在且未删除
        cursor.execute(
            "SELECT id FROM cases WHERE id = %s AND status = 1",
            (case_id,)
        )
        case = cursor.fetchone()
        
        if not case:
            return jsonify({'success': False, 'error': '案件不存在或已被删除'}), 404
        
        # 执行软删除
        cursor.execute(
            "UPDATE cases SET status = 0 WHERE id = %s",
            (case_id,)
        )
        conn.commit()
        return jsonify({'success': True, 'message': '案件已删除'})
    except Exception as e:
        conn.rollback()
        logger.error(f"删除案件失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cases/<int:case_id>/applicants', methods=['GET'])
def get_applicants(case_id):
    """获取案件的所有申请人"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM applicants WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        applicants = cursor.fetchall()
        return jsonify({'success': True, 'data': applicants})
    except Exception as e:
        logger.error(f"获取申请人列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/applicants/<int:applicant_id>', methods=['GET'])
def get_applicant_detail(applicant_id):
    """获取单个申请人详情（包含仲裁请求）"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM applicants WHERE id = %s",
            (applicant_id,)
        )
        applicant = cursor.fetchone()
        
        if not applicant:
            return jsonify({'success': False, 'error': '申请人不存在'}), 404
        
        cursor.execute(
            "SELECT seq_no, content FROM arbitration_requests WHERE applicant_id = %s ORDER BY seq_no",
            (applicant_id,)
        )
        applicant['requests'] = cursor.fetchall()
        
        return jsonify({'success': True, 'data': applicant})
    except Exception as e:
        logger.error(f"获取申请人详情失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/applicants/<int:applicant_id>/requests', methods=['GET'])
def get_applicant_requests(applicant_id):
    """获取申请人的仲裁请求"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM arbitration_requests WHERE applicant_id = %s ORDER BY seq_no",
            (applicant_id,)
        )
        requests = cursor.fetchall()
        return jsonify({'success': True, 'data': requests})
    except Exception as e:
        logger.error(f"获取仲裁请求失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cases/<int:case_id>/respondents', methods=['GET'])
def get_respondents(case_id):
    """获取案件的所有被申请人"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM respondents WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        respondents = cursor.fetchall()
        return jsonify({'success': True, 'data': respondents})
    except Exception as e:
        logger.error(f"获取被申请人列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cases/<int:case_id>/evidence', methods=['GET'])
def get_evidence(case_id):
    """获取案件的所有证据"""
    conn = get_labor_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM evidence WHERE case_id = %s ORDER BY seq_no",
            (case_id,)
        )
        evidence = cursor.fetchall()
        return jsonify({'success': True, 'data': evidence})
    except Exception as e:
        logger.error(f"获取证据列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ============================================
# 错误处理
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': 'API端点不存在',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'code': 405,
        'message': '请求方法不允许',
        'timestamp': datetime.now().isoformat()
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"服务器内部错误: {str(error)}")
    return jsonify({
        'code': 500,
        'message': '服务器内部错误',
        'timestamp': datetime.now().isoformat()
    }), 500


# ============================================
# 健康检查
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


# ============================================
# 启动服务器
# ============================================

def start_server():
    """启动服务器"""
    logger.info("=" * 60)
    logger.info("劳动仲裁信息查询综合服务平台启动")
    logger.info("=" * 60)
    logger.info(f"服务地址: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info(f"页面访问: http://<服务器IP>:{Config.FLASK_PORT}/")
    logger.info(f"案件查询: http://<服务器IP>:{Config.FLASK_PORT}/query")
    logger.info("=" * 60)
    logger.info("API端点列表:")
    logger.info("  [页面服务]")
    logger.info("  GET  /              - 劳动仲裁申请书在线填写（支持编辑: ?case_id=xxx）")
    logger.info("  GET  /query         - 案件查询页面")
    logger.info("  GET  /cases         - 案件管理列表")
    logger.info("  [内部API服务]")
    logger.info("  GET  /api/status    - 服务状态")
    logger.info("  GET  /api/login/status    - 登录状态")
    logger.info("  POST /api/login           - 手动登录")
    logger.info("  POST /api/company/query   - 查询企业信息")
    logger.info("  POST /api/idcard/query    - 查询身份证信息")
    logger.info("  GET  /api/db/status       - 数据库状态")
    logger.info("  [案件管理API]")
    logger.info("  POST /api/cases/save      - 保存案件")
    logger.info("  GET  /api/cases/query     - 查询案件")
    logger.info("  GET  /api/cases/list      - 案件列表")
    logger.info("  DELETE /api/cases/<id>    - 删除案件")
    logger.info("=" * 60)
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
        threaded=True
    )


if __name__ == '__main__':
    start_server()
