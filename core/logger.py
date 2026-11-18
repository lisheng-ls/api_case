import sys
from pathlib import Path
from datetime import datetime
from loguru import logger


class LogUtil:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._setup_logger()

    @staticmethod
    def _serialize_record(record):
        """处理record里datetime对象，避免序列化报错"""
        for k, v in record["extra"].items():
            if isinstance(v, datetime):
                record["extra"][k] = v.isoformat()
        return record

    def _setup_logger(self):
        # 移除默认handler
        logger.remove()

        log_dir = r'D:\学习项目\PythonProject\logs'
        log_dir_path = Path(log_dir)
        if not log_dir_path.exists():
            log_dir_path.mkdir(exist_ok=True, parents=True)

        # 日志格式
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # 控制台输出
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG",
            filter=self._serialize_record
        )

        # 文件日志：按50MB切割，最多保留10个文件
        logger.add(
            log_dir_path / "app_{time:YYYY-MM-DD}.log",
            format=log_format,
            rotation="50 MB",
            retention="10 days",
            encoding="utf-8",
            level="INFO",
            filter=self._serialize_record,
            enqueue=True  # 多线程安全
        )

    @property
    def log(self):
        return logger


# 全局单例
log_util = LogUtil()
log = log_util.log
