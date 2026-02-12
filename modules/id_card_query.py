# 身份证查询模块
import requests
import json
import logging
from config import Config
from login_manager import get_login_manager
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IDCardQueryManager:
    """身份证查询管理器"""
    
    def __init__(self):
        self.config = Config
        self.login_manager = get_login_manager()
        self.db_manager = get_db_manager()
        self.id_card_query_url = "http://10.96.10.78:8080/v1/api/admin/datashare/openPlatformProxy/api/SJCK_idCardInfo"
    
    def query_id_card(self, id_card_number):
        """
        查询身份证信息（支持缓存）
        
        Args:
            id_card_number (str): 身份证号码
            
        Returns:
            dict: 查询结果
        """
        try:
            logger.info(f"执行身份证查询: {id_card_number} (先查缓存)")
            
            # 第一步：先从缓存中查询
            cached_data = self.db_manager.get_idcard_cache(id_card_number)
            
            if cached_data is not None:
                logger.info(f"从缓存返回身份证信息: {id_card_number}")
                return {
                    'code': 200,
                    'message': '查询成功(来自缓存)',
                    'data': cached_data,
                    'source': 'cache'
                }
            
            # 第二步：缓存中没有，调用API查询
            # 检查和更新登录状态
            if not self.login_manager.check_and_renew_login():
                logger.error("获取有效登录信息失败")
                return {
                    'code': 401,
                    'message': '获取有效登录信息失败',
                    'data': None
                }
            
            # 获取带认证信息的请求头
            headers = self.login_manager.get_auth_headers()
            if not headers:
                logger.error("获取认证请求头失败")
                return {
                    'code': 401,
                    'message': '获取认证请求头失败',
                    'data': None
                }
            
            # 构建请求体
            payload = {
                "AAC147": id_card_number
            }
            
            logger.info(f"从API查询身份证信息: {id_card_number}")
            
            # 发送请求
            response = requests.post(
                self.id_card_query_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            if result.get('code') == 200:
                personal_data = result.get('data')
                logger.info(f"身份证查询成功: {id_card_number}")
                
                # 第三步：将结果保存到缓存（30天过期）
                if personal_data:
                    self.db_manager.save_idcard_cache(id_card_number, personal_data, cache_days=30)
                
                return {
                    'code': 200,
                    'message': '查询成功',
                    'data': personal_data,
                    'source': 'api'
                }
            else:
                error_msg = result.get('message', '查询失败')
                logger.warning(f"身份证查询返回错误: {error_msg}")
                return {
                    'code': result.get('code', 500),
                    'message': error_msg,
                    'data': None
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"身份证查询请求失败: {str(e)}")
            return {
                'code': 500,
                'message': f'请求失败: {str(e)}',
                'data': None
            }
        except json.JSONDecodeError as e:
            logger.error(f"身份证查询响应JSON解析失败: {str(e)}")
            return {
                'code': 500,
                'message': f'响应JSON解析失败: {str(e)}',
                'data': None
            }
        except Exception as e:
            logger.error(f"身份证查询异常: {str(e)}")
            return {
                'code': 500,
                'message': f'系统错误: {str(e)}',
                'data': None
            }


# 单例实例
_id_card_query_instance = None

def get_id_card_query_manager():
    """获取身份证查询管理器单例"""
    global _id_card_query_instance
    if _id_card_query_instance is None:
        _id_card_query_instance = IDCardQueryManager()
    return _id_card_query_instance
