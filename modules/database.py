# 数据库操作模块
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.config = Config
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                charset='utf8mb4',
                autocommit=True,
                connection_timeout=30
            )
            logger.info("数据库连接成功")
            self._create_table_if_not_exists()
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            self.connection = None
    
    def _ensure_connection(self):
        """确保数据库连接有效，如果连接丢失则重新连接"""
        try:
            if self.connection is None:
                logger.warning("数据库连接已断开，尝试重新连接...")
                self._init_database()
            else:
                # 测试连接是否仍有效
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
        except Error as e:
            logger.warning(f"数据库连接检查失败，准备重新连接: {e}")
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.close()
            except:
                pass
            self._init_database()
    
    def _create_table_if_not_exists(self):
        """创建所需的表（如果不存在）"""
        # 创建登录表
        create_login_table_sql = """
        CREATE TABLE IF NOT EXISTS `login` (
          `用户名` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
          `密码` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
          `authKey` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
          `sessionId` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
          `过期时间` timestamp(6) NULL DEFAULT NULL
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;
        """
        
        # 创建企业信息缓存表
        create_company_cache_table_sql = """
        CREATE TABLE IF NOT EXISTS `company_cache` (
          `id` INT AUTO_INCREMENT PRIMARY KEY,
          `company_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
          `company_data` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
          `created_time` timestamp DEFAULT CURRENT_TIMESTAMP,
          `expiry_time` timestamp NULL DEFAULT NULL,
          `query_count` INT DEFAULT 0,
          UNIQUE KEY `unique_company_name` (`company_name`),
          INDEX `idx_expiry_time` (`expiry_time`)
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;
        """
        
        # 创建个人信息缓存表
        create_idcard_cache_table_sql = """
        CREATE TABLE IF NOT EXISTS `idcard_cache` (
          `id` INT AUTO_INCREMENT PRIMARY KEY,
          `id_card_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
          `personal_data` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
          `created_time` timestamp DEFAULT CURRENT_TIMESTAMP,
          `expiry_time` timestamp NULL DEFAULT NULL,
          `query_count` INT DEFAULT 0,
          UNIQUE KEY `unique_id_card_number` (`id_card_number`),
          INDEX `idx_expiry_time` (`expiry_time`)
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;
        """
        
        # 创建案件主表
        create_cases_table_sql = """
        CREATE TABLE IF NOT EXISTS `cases` (
          `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          `receipt_number` VARCHAR(50) NOT NULL,
          `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          `status` TINYINT DEFAULT 1 COMMENT '状态: 0-删除, 1-正常',
          UNIQUE KEY `uk_receipt_number` (`receipt_number`),
          INDEX `idx_create_time` (`create_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 创建申请人表
        create_applicants_table_sql = """
        CREATE TABLE IF NOT EXISTS `applicants` (
          `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          `case_id` BIGINT UNSIGNED NOT NULL,
          `seq_no` INT UNSIGNED DEFAULT 1,
          `name` VARCHAR(50) NOT NULL,
          `gender` VARCHAR(10),
          `nation` VARCHAR(20),
          `birth_date` VARCHAR(20),
          `address` TEXT,
          `phone` VARCHAR(20),
          `id_card` VARCHAR(18),
          `employment_date` VARCHAR(20),
          `work_location` VARCHAR(200),
          `monthly_salary` VARCHAR(50),
          `facts_reasons` TEXT,
          `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
          INDEX `idx_case_id` (`case_id`),
          INDEX `idx_id_card` (`id_card`),
          INDEX `idx_name` (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 创建仲裁请求表
        create_requests_table_sql = """
        CREATE TABLE IF NOT EXISTS `arbitration_requests` (
          `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          `applicant_id` BIGINT UNSIGNED NOT NULL,
          `case_id` BIGINT UNSIGNED NOT NULL,
          `seq_no` INT UNSIGNED DEFAULT 1,
          `content` TEXT NOT NULL,
          `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (`applicant_id`) REFERENCES `applicants`(`id`) ON DELETE CASCADE,
          FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
          INDEX `idx_applicant_id` (`applicant_id`),
          INDEX `idx_case_id` (`case_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 创建被申请人表
        create_respondents_table_sql = """
        CREATE TABLE IF NOT EXISTS `respondents` (
          `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          `case_id` BIGINT UNSIGNED NOT NULL,
          `seq_no` INT UNSIGNED DEFAULT 1,
          `name` VARCHAR(200) NOT NULL,
          `legal_person` VARCHAR(50),
          `position` VARCHAR(50),
          `address` TEXT,
          `phone` VARCHAR(20),
          `unified_code` VARCHAR(50),
          `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
          INDEX `idx_case_id` (`case_id`),
          INDEX `idx_unified_code` (`unified_code`),
          INDEX `idx_name` (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 创建证据表
        create_evidence_table_sql = """
        CREATE TABLE IF NOT EXISTS `evidence` (
          `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          `case_id` BIGINT UNSIGNED NOT NULL,
          `applicant_id` BIGINT UNSIGNED NULL,
          `seq_no` INT UNSIGNED DEFAULT 1,
          `name` VARCHAR(200) NOT NULL,
          `source` VARCHAR(100),
          `purpose` TEXT,
          `page_start` VARCHAR(10),
          `page_end` VARCHAR(10),
          `page_range` VARCHAR(50),
          `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
          FOREIGN KEY (`applicant_id`) REFERENCES `applicants`(`id`) ON DELETE SET NULL,
          INDEX `idx_case_id` (`case_id`),
          INDEX `idx_applicant_id` (`applicant_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            cursor = self.connection.cursor()
            
            # 创建登录表
            cursor.execute(create_login_table_sql)
            logger.info("登录表检查/创建完成")
            
            # 创建企业信息缓存表
            cursor.execute(create_company_cache_table_sql)
            logger.info("企业信息缓存表检查/创建完成")
            
            # 创建个人信息缓存表
            cursor.execute(create_idcard_cache_table_sql)
            logger.info("个人信息缓存表检查/创建完成")
            
            # 创建案件相关表
            cursor.execute(create_cases_table_sql)
            logger.info("案件表检查/创建完成")
            
            cursor.execute(create_applicants_table_sql)
            logger.info("申请人表检查/创建完成")
            
            cursor.execute(create_requests_table_sql)
            logger.info("仲裁请求表检查/创建完成")
            
            cursor.execute(create_respondents_table_sql)
            logger.info("被申请人表检查/创建完成")
            
            cursor.execute(create_evidence_table_sql)
            logger.info("证据表检查/创建完成")
            
            self.connection.commit()
            cursor.close()
        except Error as e:
            logger.error(f"创建表失败: {e}")
    
    def save_login_info(self, username, password, auth_key, session_id):
        """保存登录信息到数据库"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return False
        
        # 计算过期时间（当前时间 + 18小时）
        expiry_time = datetime.now() + timedelta(hours=self.config.SESSION_EXPIRY_HOURS)
        
        # 先删除该用户的旧记录
        delete_sql = "DELETE FROM `login` WHERE `用户名` = %s"
        
        # 插入新记录
        insert_sql = """
        INSERT INTO `login` (`用户名`, `密码`, `authKey`, `sessionId`, `过期时间`)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            cursor = self.connection.cursor()
            
            # 删除旧记录
            cursor.execute(delete_sql, (username,))
            
            # 插入新记录
            cursor.execute(insert_sql, (username, password, auth_key, session_id, expiry_time))
            
            self.connection.commit()
            cursor.close()
            logger.info(f"登录信息保存成功: {username}")
            return True
        except Error as e:
            logger.error(f"保存登录信息失败: {e}")
            return False
    
    def get_valid_login_info(self, username):
        """获取有效的登录信息（检查是否过期）"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return None
        
        query_sql = """
        SELECT `用户名`, `密码`, `authKey`, `sessionId`, `过期时间`
        FROM `login`
        WHERE `用户名` = %s AND `过期时间` > NOW()
        ORDER BY `过期时间` DESC
        LIMIT 1
        """
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query_sql, (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                logger.info(f"找到有效的登录信息: {username}")
                return {
                    'username': result['用户名'],
                    'password': result['密码'],
                    'authKey': result['authKey'],
                    'sessionId': result['sessionId'],
                    'expiry_time': result['过期时间']
                }
            else:
                logger.info(f"未找到有效的登录信息: {username}")
                return None
        except Error as e:
            logger.error(f"查询登录信息失败: {e}")
            return None
    
    def is_login_expired(self, username):
        """检查登录是否过期"""
        login_info = self.get_valid_login_info(username)
        return login_info is None
    
    def delete_expired_logins(self):
        """删除过期的登录记录"""
        if not self.connection:
            logger.error("数据库未连接")
            return False
        
        delete_sql = "DELETE FROM `login` WHERE `过期时间` <= NOW()"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_sql)
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            if deleted_count > 0:
                logger.info(f"删除了 {deleted_count} 条过期的登录记录")
            return deleted_count
        except Error as e:
            logger.error(f"删除过期记录失败: {e}")
            return False
    
    def get_all_logins(self):
        """获取所有登录记录（用于调试）"""
        if not self.connection:
            logger.error("数据库未连接")
            return []
        
        query_sql = """
        SELECT `用户名`, `authKey`, `sessionId`, `过期时间`
        FROM `login`
        ORDER BY `过期时间` DESC
        """
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query_sql)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"获取所有登录记录失败: {e}")
            return []
    
    # ================== 企业信息缓存操作 ==================
    
    def save_company_cache(self, company_name, company_data, cache_days=30):
        """保存企业信息到缓存"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return False
        
        # 计算过期时间（当前时间 + cache_days天）
        expiry_time = datetime.now() + timedelta(days=cache_days)
        
        # 如果记录存在则更新，不存在则插入
        check_sql = "SELECT id FROM `company_cache` WHERE `company_name` = %s"
        insert_sql = """
        INSERT INTO `company_cache` (`company_name`, `company_data`, `expiry_time`, `query_count`)
        VALUES (%s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE
            `company_data` = VALUES(`company_data`),
            `expiry_time` = VALUES(`expiry_time`),
            `query_count` = `query_count` + 1,
            `created_time` = CURRENT_TIMESTAMP
        """
        
        try:
            import json
            cursor = self.connection.cursor()
            
            # 将数据转为JSON字符串存储
            company_data_json = json.dumps(company_data, ensure_ascii=False, default=str)
            
            cursor.execute(insert_sql, (company_name, company_data_json, expiry_time))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"企业信息已缓存: {company_name}")
            return True
        except Error as e:
            logger.error(f"保存企业缓存失败: {e}")
            return False
    
    def get_company_cache(self, company_name):
        """从缓存获取企业信息"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return None
        
        # 先删除过期的缓存
        self.delete_expired_company_cache()
        
        query_sql = """
        SELECT `company_data`, `expiry_time`
        FROM `company_cache`
        WHERE `company_name` = %s AND `expiry_time` > NOW()
        LIMIT 1
        """
        
        try:
            import json
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query_sql, (company_name,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                logger.info(f"从缓存获取企业信息: {company_name}")
                company_data = json.loads(result['company_data'])
                return company_data
            else:
                logger.info(f"缓存中未找到企业信息: {company_name}")
                return None
        except Error as e:
            logger.error(f"获取企业缓存失败: {e}")
            return None
    
    def delete_expired_company_cache(self):
        """删除过期的企业信息缓存"""
        if not self.connection:
            logger.error("数据库未连接")
            return 0
        
        delete_sql = "DELETE FROM `company_cache` WHERE `expiry_time` <= NOW()"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_sql)
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            if deleted_count > 0:
                logger.info(f"删除了 {deleted_count} 条过期的企业缓存记录")
            return deleted_count
        except Error as e:
            logger.error(f"删除过期企业缓存失败: {e}")
            return 0
    
    # ================== 个人信息缓存操作 ==================
    
    def save_idcard_cache(self, id_card_number, personal_data, cache_days=30):
        """保存个人信息到缓存"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return False
        
        # 计算过期时间（当前时间 + cache_days天）
        expiry_time = datetime.now() + timedelta(days=cache_days)
        
        # 如果记录存在则更新，不存在则插入
        insert_sql = """
        INSERT INTO `idcard_cache` (`id_card_number`, `personal_data`, `expiry_time`, `query_count`)
        VALUES (%s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE
            `personal_data` = VALUES(`personal_data`),
            `expiry_time` = VALUES(`expiry_time`),
            `query_count` = `query_count` + 1,
            `created_time` = CURRENT_TIMESTAMP
        """
        
        try:
            import json
            cursor = self.connection.cursor()
            
            # 将数据转为JSON字符串存储
            personal_data_json = json.dumps(personal_data, ensure_ascii=False, default=str)
            
            cursor.execute(insert_sql, (id_card_number, personal_data_json, expiry_time))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"个人信息已缓存: {id_card_number}")
            return True
        except Error as e:
            logger.error(f"保存个人缓存失败: {e}")
            return False
    
    def get_idcard_cache(self, id_card_number):
        """从缓存获取个人信息"""
        self._ensure_connection()
        if not self.connection:
            logger.error("数据库未连接")
            return None
        
        # 先删除过期的缓存
        self.delete_expired_idcard_cache()
        
        query_sql = """
        SELECT `personal_data`, `expiry_time`
        FROM `idcard_cache`
        WHERE `id_card_number` = %s AND `expiry_time` > NOW()
        LIMIT 1
        """
        
        try:
            import json
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query_sql, (id_card_number,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                logger.info(f"从缓存获取个人信息: {id_card_number}")
                personal_data = json.loads(result['personal_data'])
                return personal_data
            else:
                logger.info(f"缓存中未找到个人信息: {id_card_number}")
                return None
        except Error as e:
            logger.error(f"获取个人缓存失败: {e}")
            return None
    
    def delete_expired_idcard_cache(self):
        """删除过期的个人信息缓存"""
        if not self.connection:
            logger.error("数据库未连接")
            return 0
        
        delete_sql = "DELETE FROM `idcard_cache` WHERE `expiry_time` <= NOW()"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_sql)
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            if deleted_count > 0:
                logger.info(f"删除了 {deleted_count} 条过期的个人缓存记录")
            return deleted_count
        except Error as e:
            logger.error(f"删除过期个人缓存失败: {e}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("数据库连接已关闭")


# 单例实例
_db_instance = None

def get_db_manager():
    """获取数据库管理器单例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
