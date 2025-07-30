"""
PeerPortal AI智能体架构 v2.0 工具辅助函数
通用的工具函数和辅助方法
"""
import uuid
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def generate_unique_id(prefix: str = "") -> str:
    """生成唯一ID"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_session_id(user_id: str) -> str:
    """生成会话ID"""
    timestamp = int(time.time())
    return f"session_{user_id}_{timestamp}_{uuid.uuid4().hex[:8]}"


def generate_hash(data: Union[str, Dict, List]) -> str:
    """生成数据哈希值"""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    elif not isinstance(data, str):
        data = str(data)
    
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def get_current_timestamp() -> float:
    """获取当前时间戳"""
    return time.time()


def get_current_datetime() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    """格式化时间"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def safe_json_loads(data: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize JSON: {e}")
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_first_n_words(text: str, n: int = 50) -> str:
    """提取前N个单词"""
    words = text.split()
    if len(words) <= n:
        return text
    return " ".join(words[:n]) + "..."


def clean_text(text: str) -> str:
    """清理文本"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = " ".join(text.split())
    # 移除特殊字符（保留基本标点）
    # text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:]', '', text)
    
    return text.strip()


def merge_dicts(*dicts: Dict) -> Dict:
    """合并多个字典"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_nested_value(data: Dict, key_path: str, default: Any = None, sep: str = '.') -> Any:
    """获取嵌套字典的值"""
    keys = key_path.split(sep)
    value = data
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict, key_path: str, value: Any, sep: str = '.') -> None:
    """设置嵌套字典的值"""
    keys = key_path.split(sep)
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def batch_process(items: List, batch_size: int = 10) -> List[List]:
    """批量处理列表"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """带退避的重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    return wrapper


async def async_retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """异步带退避的重试装饰器"""
    import asyncio
    
    def wrapper(*args, **kwargs):
        async def async_wrapper():
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
        
        return async_wrapper()
    
    return wrapper


def validate_config(config: Dict, required_keys: List[str]) -> bool:
    """验证配置"""
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logger.error(f"Missing required config keys: {missing_keys}")
        return False
    return True


def log_performance(func_name: str, start_time: float, end_time: float, **kwargs):
    """记录性能指标"""
    duration = end_time - start_time
    log_data = {
        "function": func_name,
        "duration": duration,
        "timestamp": get_current_timestamp(),
        **kwargs
    }
    logger.info(f"Performance: {log_data}")


class Timer:
    """简单的计时器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """停止计时"""
        self.end_time = time.time()
        return self
    
    def elapsed(self) -> float:
        """获取耗时"""
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# 便捷函数
def create_timer() -> Timer:
    """创建计时器"""
    return Timer()


def is_valid_uuid(uuid_string: str) -> bool:
    """检查UUID是否有效"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮盖敏感数据"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


# 常用常量
DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT = 30
DEFAULT_BATCH_SIZE = 10
MAX_TEXT_LENGTH = 1000
MAX_RETRY_ATTEMPTS = 3 