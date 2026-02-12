# 企业查询模块
import requests
import json
import logging
from datetime import datetime
from config import Config
from login_manager import get_login_manager
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyQuery:
    """企业查询器"""
    
    def __init__(self):
        self.config = Config
        self.login_manager = get_login_manager()
        self.db_manager = get_db_manager()
    
    def query_company_info(self, company_name, exact_match=True):
        """
        查询企业信息（支持缓存）
        
        Args:
            company_name: 企业名称
            exact_match: 是否精确匹配（True: 精确匹配，False: 模糊匹配）
            
        Returns:
            dict: 查询结果
        """
        # 第一步：先从缓存中查询
        logger.info(f"查询企业信息: {company_name} (先查缓存)")
        cached_data = self.db_manager.get_company_cache(company_name)
        
        if cached_data is not None:
            logger.info(f"从缓存返回企业信息: {company_name}")
            return {
                'code': 200,
                'message': '查询成功(来自缓存)',
                'data': cached_data,
                'total_count': len(cached_data) if isinstance(cached_data, list) else 1,
                'matched_count': len(cached_data) if isinstance(cached_data, list) else 1,
                'source': 'cache'
            }
        
        # 第二步：缓存中没有，调用API查询
        # 检查并更新登录状态
        if not self.login_manager.check_and_renew_login():
            return {
                'code': 401,
                'message': '登录失败，无法查询企业信息',
                'data': None
            }
        
        # 获取认证头信息
        headers = self.login_manager.get_auth_headers()
        if not headers:
            return {
                'code': 401,
                'message': '获取认证信息失败',
                'data': None
            }
        
        # 构建请求体
        payload = {"CNNAME": company_name}
        
        try:
            logger.info(f"从API查询企业信息: {company_name}")
            
            response = requests.post(
                self.config.COMPANY_QUERY_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 处理查询结果
            if result.get('code') == 200:
                data = result.get('data', [])
                
                if not isinstance(data, list):
                    data = []
                
                # 根据匹配模式过滤结果
                filtered_data = []
                if exact_match:
                    # 精确匹配
                    for item in data:
                        if isinstance(item, dict) and item.get('CNNAME') == company_name:
                            filtered_data.append(item)
                else:
                    # 模糊匹配（包含查询字符串）
                    for item in data:
                        if isinstance(item, dict) and company_name in item.get('CNNAME', ''):
                            filtered_data.append(item)
                
                if filtered_data:
                    logger.info(f"找到 {len(filtered_data)} 条匹配记录")
                    
                    # 第三步：将结果保存到缓存（30天过期）
                    self.db_manager.save_company_cache(company_name, filtered_data, cache_days=30)
                    
                    return {
                        'code': 200,
                        'message': '查询成功',
                        'data': filtered_data,
                        'total_count': len(data),
                        'matched_count': len(filtered_data),
                        'source': 'api'
                    }
                else:
                    logger.info(f"未找到匹配记录，共返回 {len(data)} 条记录")
                    return {
                        'code': 404,
                        'message': '未找到匹配的企业信息',
                        'data': None,
                        'total_count': len(data),
                        'matched_count': 0,
                        'source': 'api'
                    }
            else:
                error_msg = result.get('message', '查询失败')
                logger.error(f"查询失败: {error_msg}")
                return {
                    'code': result.get('code', 500),
                    'message': error_msg,
                    'data': None
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"查询请求失败: {str(e)}")
            return {
                'code': 500,
                'message': f'查询请求失败: {str(e)}',
                'data': None
            }
        except json.JSONDecodeError as e:
            logger.error(f"查询响应JSON解析失败: {str(e)}")
            return {
                'code': 500,
                'message': f'查询响应JSON解析失败: {str(e)}',
                'data': None
            }
    
    def format_company_info(self, company_data):
        """
        格式化企业信息为易读的格式
        
        Args:
            company_data: 企业信息字典
            
        Returns:
            dict: 格式化后的企业信息
        """
        if not company_data:
            return None
        
        # 定义字段的中文名称映射
        field_names = {
            "SCJYDZ": "实际经营地址",
            "INDURSTRYNAME": "行业名称",
            "COMPANYTYPE": "公司类型",
            "QYTYPE": "企业类型",
            "TYSHXYDM": "统一社会信用代码",
            "REGADDRESS": "注册地址",
            "MANAGEBEGINDATE": "经营开始日期",
            "MANAGEENDDATE": "经营结束日期",
            "ESTABLISHDATE": "成立日期",
            "REGISTERSTATE": "注册状态",
            "CNNAME": "企业名称",
            "LEGALPERSONNAME": "法人姓名",
            "REGFUNDAMOUNT": "注册资本（万元）",
            "COMPANYPHONE": "公司电话",
            "PROVEINS": "证明机构",
            "ESTABLISHWAY": "成立方式",
            "GSZCH": "工商注册号"
        }
        
        formatted_data = {}
        
        # 处理每个字段
        for key, chinese_name in field_names.items():
            value = company_data.get(key)
            if value is not None:
                # 处理日期格式
                if key == "ESTABLISHDATE" and isinstance(value, int):
                    # 将毫秒时间戳转换为日期
                    try:
                        dt = datetime.fromtimestamp(value / 1000)
                        value = dt.strftime("%Y-%m-%d")
                    except:
                        pass
                
                formatted_data[chinese_name] = value
        
        return formatted_data
    
    def query_multiple_companies(self, company_names, exact_match=True):
        """
        批量查询多个企业
        
        Args:
            company_names: 企业名称列表
            exact_match: 是否精确匹配
            
        Returns:
            dict: 批量查询结果
        """
        results = {
            'code': 200,
            'message': '批量查询完成',
            'total_companies': len(company_names),
            'successful_queries': 0,
            'failed_queries': 0,
            'results': []
        }
        
        for i, company_name in enumerate(company_names, 1):
            logger.info(f"批量查询 [{i}/{len(company_names)}]: {company_name}")
            
            query_result = self.query_company_info(company_name, exact_match)
            
            result_item = {
                'company_name': company_name,
                'query_result': query_result
            }
            
            if query_result.get('code') == 200:
                results['successful_queries'] += 1
            else:
                results['failed_queries'] += 1
            
            results['results'].append(result_item)
        
        return results
    
    def get_query_status(self):
        """
        获取查询状态信息
        
        Returns:
            dict: 状态信息
        """
        login_status = self.login_manager.get_login_status()
        
        return {
            'query_service': 'running',
            'login_status': login_status,
            'api_endpoint': self.config.COMPANY_QUERY_URL,
            'timestamp': datetime.now().isoformat()
        }


# 单例实例
_company_query_instance = None

def get_company_query():
    """获取企业查询器单例"""
    global _company_query_instance
    if _company_query_instance is None:
        _company_query_instance = CompanyQuery()
    return _company_query_instance
