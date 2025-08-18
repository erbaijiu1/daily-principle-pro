import logging
from logging.handlers import RotatingFileHandler
from config import GLOBAL_LOG_PATH

def setup_logger(name, log_file=GLOBAL_LOG_PATH, level=logging.DEBUG):
    """设置日志记录器"""
    # formatter = logging.Formatter('%(asctime)s|[%(filename)s: %(lineno)d]|%(levelname)s|%(message)s ')
    formatter = logging.Formatter('%(asctime)s|[%(filename)s: %(lineno)d]|%(levelname)s|%(thread)d|%(message)s ')

    # 创建一个滚动文件处理器
    file_handler = RotatingFileHandler(log_file, maxBytes=500*1024*1024, backupCount=20)
    file_handler.setFormatter(formatter)

    # 创建一个标准输出处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 创建一个日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)  # 添加标准输出处理器

    return logger

logger = setup_logger(__name__)
