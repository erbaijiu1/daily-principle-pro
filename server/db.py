import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from utils.logger_config import logger
from urllib.parse import quote

# 获取当前文件所在目录作为项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录

# 数据库文件路径：项目根目录下的 server_data/prize_cal.db
db_dir = os.path.join(BASE_DIR, "server_data")
db_file = os.path.join(db_dir, "prize_cal.db")


class DatabaseManager:
    _engine = None

    @classmethod
    def get_db_engine(cls):
        if cls._engine is None:
            # URL 编码密码
            encoded_password = quote(DB_PASSWORD)# URL 编码密码
            engine_url = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

            # 脱敏处理
            masked_url = engine_url.replace(engine_url.split(":")[2].split("@")[0], "****:****")
            logger.info(f"数据库引擎已创建: {masked_url}")
            try:
                cls._engine = create_engine(
                    engine_url,
                    pool_size=10,  # 根据实际需求调整
                    pool_recycle=1800  # 根据实际需求调整
                )
            except Exception as e:
                logger.error(f"数据库引擎创建失败: {e}")
                raise
        return cls._engine

    @classmethod
    def get_sqlite_engine(cls):

        if cls._engine is None:
            # engine_url = "sqlite:///server_data/prize_cal.db"
            engine_url = f"sqlite:///{db_file}"
            logger.info(f"数据库引擎已创建: {engine_url}")
            try:
                cls._engine = create_engine(
                    engine_url,
                    connect_args={"check_same_thread": False}  # 适用于 SQLite 多线程操作
                )
            except Exception as e:
                logger.error(f"数据库引擎创建失败: {e}")
                raise
        return cls._engine

def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=DatabaseManager.get_db_engine())

SessionLocal = sessionmaker(bind=DatabaseManager.get_db_engine(), autocommit=False, autoflush=False)

def get_db():
    """FastAPI 依赖注入专用，每次请求自动获取并关闭 session"""
    db_session = get_session_factory()()
    try:
        yield db_session
    finally:
        db_session.close()


