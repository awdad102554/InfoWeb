# 登录管理模块
import requests
import json
import logging
from datetime import datetime, timedelta
from config import Config
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginManager:
    """登录管理器"""
    
    def __init__(self):
        self.config = Config
        self.db_manager = get_db_manager()
        self.current_auth_key = None
        self.current_session_id = None
    
    def login(self, force=False):
        """
        执行登录操作
        
        Args:
            force: 是否强制重新登录（即使有有效会话）
            
        Returns:
            dict: 登录结果，包含authKey和sessionId
        """
        username = self.config.LOGIN_USERNAME
        password = self.config.LOGIN_PASSWORD
        
        # 检查是否有有效的登录信息（除非强制重新登录）
        if not force:
            try:
                valid_login = self.db_manager.get_valid_login_info(username)
                if valid_login:
                    logger.info("使用缓存的登录信息")
                    self.current_auth_key = valid_login['authKey']
                    self.current_session_id = valid_login['sessionId']
                    return {
                        'code': 200,
                        'message': '使用缓存的登录信息',
                        'authKey': self.current_auth_key,
                        'sessionId': self.current_session_id,
                        'expiry_time': valid_login['expiry_time'].isoformat() if valid_login['expiry_time'] else None
                    }
            except Exception as e:
                logger.warning(f"从数据库获取登录信息失败，将重新登录: {e}")
        
        # 执行登录请求
        logger.info(f"执行登录请求: {username}")
        
        # 构建请求体
        payload = {
            "username": username,
            "password": password
        }
        
        # 构建请求头
        headers = self.config.DEFAULT_HEADERS.copy()
        
        try:
            response = requests.post(
                self.config.LOGIN_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            if result.get('code') == 200:
                # 提取登录信息
                data = result.get('data', {})
                auth_key = data.get('authKey')
                session_id = data.get('sessionId')
                
                if auth_key and session_id:
                    self.current_auth_key = auth_key
                    self.current_session_id = session_id
                    
                    # 尝试保存到数据库（失败不影响登录）
                    try:
                        self.db_manager.save_login_info(username, password, auth_key, session_id)
                    except Exception as e:
                        logger.warning(f"保存登录信息到数据库失败: {e}")
                    
                    logger.info(f"登录成功: {username}")
                    return {
                        'code': 200,
                        'message': '登录成功',
                        'authKey': auth_key,
                        'sessionId': session_id,
                        'expiry_time': (datetime.now() + timedelta(hours=self.config.SESSION_EXPIRY_HOURS)).isoformat()
                    }
                else:
                    logger.error("登录响应中缺少authKey或sessionId")
                    return {
                        'code': 500,
                        'message': '登录响应中缺少authKey或sessionId',
                        'authKey': None,
                        'sessionId': None
                    }
            else:
                error_msg = result.get('message', '登录失败')
                logger.error(f"登录失败: {error_msg}")
                return {
                    'code': result.get('code', 500),
                    'message': error_msg,
                    'authKey': None,
                    'sessionId': None
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"登录请求失败: {str(e)}")
            return {
                'code': 500,
                'message': f'登录请求失败: {str(e)}',
                'authKey': None,
                'sessionId': None
            }
        except json.JSONDecodeError as e:
            logger.error(f"登录响应JSON解析失败: {str(e)}")
            return {
                'code': 500,
                'message': f'登录响应JSON解析失败: {str(e)}',
                'authKey': None,
                'sessionId': None
            }
    
    def get_auth_headers(self, force_login=False):
        """
        获取包含认证信息的请求头
        
        Args:
            force_login: 是否强制重新登录
            
        Returns:
            dict: 包含认证信息的请求头，或None如果登录失败
        """
        # 如果强制登录或者当前没有有效的登录信息，执行登录
        if force_login or not self.current_auth_key or not self.current_session_id:
            login_result = self.login(force=force_login)
            if login_result['code'] != 200:
                return None
        
        # 构建带有认证信息的请求头
        headers = self.config.DEFAULT_HEADERS.copy()
        headers['authKey'] = self.current_auth_key
        headers['sessionId'] = self.current_session_id
        
        return headers
    
    def check_and_renew_login(self):
        """
        检查登录状态并在过期时重新登录
        
        Returns:
            bool: 是否成功获取有效的登录信息
        """
        username = self.config.LOGIN_USERNAME
        
        try:
            # 检查登录是否过期
            if self.db_manager.is_login_expired(username):
                logger.info("登录已过期，重新登录...")
                login_result = self.login(force=True)
                return login_result['code'] == 200
            else:
                # 确保当前有有效的登录信息
                if not self.current_auth_key or not self.current_session_id:
                    valid_login = self.db_manager.get_valid_login_info(username)
                    if valid_login:
                        self.current_auth_key = valid_login['authKey']
                        self.current_session_id = valid_login['sessionId']
                        logger.info("已加载有效的登录信息")
                        return True
                    else:
                        logger.warning("数据库中有记录但加载失败，尝试重新登录")
                        login_result = self.login(force=True)
                        return login_result['code'] == 200
                return True
        except Exception as e:
            logger.warning(f"检查登录状态时出错: {e}，尝试重新登录")
            login_result = self.login(force=True)
            return login_result['code'] == 200
    
    def get_login_status(self):
        """
        获取当前登录状态
        
        Returns:
            dict: 登录状态信息
        """
        username = self.config.LOGIN_USERNAME
        valid_login = self.db_manager.get_valid_login_info(username)
        
        status = {
            'username': username,
            'is_logged_in': False,
            'has_valid_session': valid_login is not None,
            'authKey': self.current_auth_key,
            'sessionId': self.current_session_id,
            'expiry_time': None,
            'remaining_hours': 0
        }
        
        if valid_login:
            status['is_logged_in'] = True
            status['expiry_time'] = valid_login['expiry_time'].isoformat() if valid_login['expiry_time'] else None
            
            # 计算剩余时间
            if valid_login['expiry_time']:
                from datetime import datetime
                remaining = valid_login['expiry_time'] - datetime.now()
                status['remaining_hours'] = round(remaining.total_seconds() / 3600, 2)
        
        return status
    
    def cleanup_expired_logins(self):
        """清理过期的登录记录"""
        return self.db_manager.delete_expired_logins()


# 单例实例
_login_instance = None

def get_login_manager():
    """获取登录管理器单例"""
    global _login_instance
    if _login_instance is None:
        _login_instance = LoginManager()
    return _login_instance
