from sqlalchemy import Column, BigInteger, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class WechatArticle(Base):
    __tablename__ = "t_wechat_articles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    url = Column(String(512), nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    author = Column(String(128), default='')
    published_at = Column(DateTime, nullable=True)
    cover_image = Column(String(512), default='')
    content_html = Column(Text, nullable=False)
    content_text = Column(Text, nullable=False)
    tag = Column(String(64), default='每日原则')
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
