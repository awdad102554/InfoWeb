# 配置文件
import os
from datetime import timedelta

class Config:
    # 数据库配置
    DB_HOST = "127.0.0.1"
    DB_PORT = 3306
    DB_NAME = "判决书生成"
    DB_USER = "root"
    DB_PASSWORD = "difydify"
    
    # API配置
    LOGIN_URL = "http://10.96.10.78:8080/v1/api/admin/login"
    COMPANY_QUERY_URL = "http://10.96.10.78:8080/v1/api/admin/datashare/openPlatformProxy/api/SJCK_businessFiveCertInfo"
    
    # 登录配置
    LOGIN_USERNAME = "huhailiang"
    LOGIN_PASSWORD = "eyJpdiI6IjFDalU2azNBY1UrVkhUazBad0ZpY3c9PSIsInZhbHVlIjoiNE16d1NHXC9ISkV0Z1ZnalFNSUZldU9hUDMwYTNNaGxhMldRU09Ic0FkeFU9IiwibWFjIjoiM2MyZjVhYWRkNjliNThhMjc4YjE2MThiMmU1NmNjMzIxYjAyMTkxM2IzZjVjN2MyNjFlNzliYTQ1NjQ5MTM3ZSJ9"
    
    # 过期时间配置（10小时）
    SESSION_EXPIRY_HOURS = 10
    
    # Flask配置
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    FLASK_DEBUG = True
    
    # 请求头配置
    DEFAULT_HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Host': '10.96.10.78:8080',
        'Origin': 'http://10.96.10.78',
        'Referer': 'http://10.96.10.78/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36 Edg/80.0.361.62'
    }
