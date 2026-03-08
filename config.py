"""
⚙️ 配置常量模块

存放所有配置相关的常量，支持环境变量覆盖
"""

import os
from typing import Optional

class ConfigManager:
    """配置管理器，支持环境变量和默认值"""
    
    @staticmethod
    def get_env_var(key: str, default: str = "") -> str:
        """获取环境变量，支持前缀"""
        # 尝试多种环境变量命名方式
        env_vars = [
            f"PHIGROS_{key}",
            f"PHIGROS_{key.upper()}",
            key,
            key.upper()
        ]
        
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value is not None:
                return value
        return default
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """获取整数配置"""
        try:
            return int(ConfigManager.get_env_var(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = ConfigManager.get_env_var(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'y', 'on')

# API 配置
BASE_URL = ConfigManager.get_env_var("BASE_URL", "https://r0semi.xtower.site/api/v1/open")
DEFAULT_API_TOKEN = ConfigManager.get_env_var("API_TOKEN", "")

# HTTP 配置
HTTP_TIMEOUT = 30
HTTP_CONNECT_TIMEOUT = 10
HTTP_SOCK_READ_TIMEOUT = 20
HTTP_POOL_SIZE = 50
HTTP_POOL_PER_HOST = 20

# 缓存配置
CACHE_TTL = 300  # 5 分钟
CACHE_CLEAN_INTERVAL = 600  # 10 分钟

# 图片配置
DEFAULT_IMAGE_QUALITY = 95
DEFAULT_IMAGE_FORMAT = "PNG"
PNG_COMPRESS_LEVEL = 1  # 1-9, 1 为最快

# 路径配置
DEFAULT_ILLUSTRATION_PATH = "./ILLUSTRATION"
DEFAULT_AVATAR_PATH = "./AVATAR"
DEFAULT_TAPTAP_VERSION = "cn"

# 搜索配置
DEFAULT_SEARCH_LIMIT = 5
DEFAULT_HISTORY_LIMIT = 10

# 渲染配置
RENDERER_WIDTH = 1200
RENDERER_HEADER_HEIGHT = 180
RENDERER_CARD_WIDTH = 360
RENDERER_CARD_HEIGHT = 100
RENDERER_CARD_MARGIN = 15

# 字体配置
FONT_CACHE_SIZE = 50

# 登录配置
QR_LOGIN_TIMEOUT = 120  # 二维码有效期 2 分钟
QR_POLL_INTERVAL = 2  # 轮询间隔 2 秒

# 更新配置
ILLUSTRATION_UPDATE_INTERVAL = 7  # 7 天检查一次更新
ILLUSTRATION_UPDATE_TIMEOUT = 300  # 5 分钟下载超时