from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional, Tuple
import logging
from db import SessionLocal
from models import WechatArticle
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import requests
from lxml import html, etree
from readability import Document
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 常量定义
DEFAULT_TAG = "每日原则"
UNNAMED_TITLE = "未命名文章"
REQUEST_TIMEOUT = 20

class CrawlReq(BaseModel):
    url: HttpUrl
    tag: Optional[str] = "principle"

# 全局异常处理器
# @router.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error"}
#     )

def extract_with_readability(page_html: str) -> Tuple[str, str, str]:
    try:
        doc = Document(page_html)
        title = doc.short_title()
        content_html = doc.summary(html_partial=True)
        tree = html.fromstring(content_html)
        text = " ".join(tree.xpath("string(.)").split())
        return title, content_html, text
    except Exception as e:
        logger.error(f"Readability extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Readability extraction failed: {str(e)}")

def parse_wechat_article(page_html: str) -> Tuple[str, str, Optional[datetime], str, str, str]:
    try:
        tree = html.fromstring(page_html)
    except Exception as e:
        logger.error(f"HTML parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTML parsing failed: {str(e)}")

    title = tree.xpath('string(//*[@id="activity-name"] | //h1[contains(@class,"rich_media_title")] | //h1)').strip()
    author = tree.xpath('string(//*[@id="js_name"] | //*[@class="rich_media_meta rich_media_meta_text"] | //*[@class="profile_nickname"])').strip()
    content_nodes = tree.xpath('//*[@id="js_content"]')

    content_html = ""
    content_text = ""

    if content_nodes:
        content_el = content_nodes[0]
        content_el.attrib.pop("style", None)
        try:
            content_html = etree.tostring(content_el, method="html", encoding="unicode")
            content_text = " ".join(content_el.xpath("string(.)").split())
        except Exception as e:
            logger.error(f"Content serialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Content serialization failed: {str(e)}")
    else:
        _t, content_html, content_text = extract_with_readability(page_html)
        if not title:
            title = _t

    cover = tree.xpath('string(//meta[@property="og:image"]/@content)')
    pub_raw = tree.xpath('string(//meta[@property="article:published_time"]/@content | //meta[@property="og:release_date"]/@content)')
    published_at = None
    if pub_raw:
        try:
            published_at = datetime.fromisoformat(pub_raw.replace('Z','+00:00')).replace(tzinfo=None)
        except Exception:
            pass

    if not title:
        t2, _, _ = extract_with_readability(page_html)
        title = t2 or UNNAMED_TITLE

    return title, author, published_at, cover, content_html, content_text

@router.post("/crawl/wechat")
async def crawl_wechat(req: CrawlReq):
    try:
        logger.info(f"Starting to crawl article from URL: {req.url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Referer": "https://mp.weixin.qq.com/"
        }
        try:
            r = requests.get(str(req.url), headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                logger.error(f"Failed to fetch URL: {req.url}, status code: {r.status_code}")
                raise HTTPException(status_code=502, detail=f"fetch failed: {r.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when fetching URL: {req.url}, error: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Network error: {str(e)}")

        title, author, published_at, cover, content_html, content_text = parse_wechat_article(r.text)

        with SessionLocal() as s:
            # 1) 先按标题去重
            exist_by_title = s.execute(
                select(WechatArticle).where(WechatArticle.title == title)
            ).scalar_one_or_none()
            if exist_by_title:
                logger.info(f"Skip insert, duplicate title: {title} (id={exist_by_title.id})")
                return {
                    "id": exist_by_title.id,
                    "title": exist_by_title.title,
                    "author": exist_by_title.author,
                    "tag": exist_by_title.tag,
                    "skipped": True,
                    "reason": "duplicate_title"
                }

            # 2) 再按 URL 去重（以防重复提交同一链接）
            exist_by_url = s.execute(
                select(WechatArticle).where(WechatArticle.url == str(req.url))
            ).scalar_one_or_none()
            if exist_by_url:
                logger.info(f"Skip insert, duplicate url: {req.url} (id={exist_by_url.id})")
                return {
                    "id": exist_by_url.id,
                    "title": exist_by_url.title,
                    "author": exist_by_url.author,
                    "tag": exist_by_url.tag,
                    "skipped": True,
                    "reason": "duplicate_url"
                }

            # 3) 新增
            art = WechatArticle(
                url=str(req.url), title=title, author=author,
                published_at=published_at, cover_image=cover,
                content_html=content_html, content_text=content_text,
                tag=req.tag or DEFAULT_TAG
            )
            s.add(art)
            s.commit()
            s.refresh(art)
            logger.info(f"Inserted article: {art.title} (id={art.id})")

        return {"id": art.id, "title": art.title, "author": art.author, "tag": art.tag, "skipped": False}

    except Exception as e:
        logger.error(f"Error in crawl_wechat: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/articles")
async def list_articles(tag: Optional[str] = Query(None), page: int = 1, size: int = 10):
    try:
        logger.info(f"Fetching articles with tag: {tag}, page: {page}, size: {size}")
        page = max(page, 1)
        size = max(min(size, 50), 1)
        with SessionLocal() as s:
            q = s.query(WechatArticle)
            if tag:
                q = q.filter(WechatArticle.tag == tag)
            total = q.count()
            rows = (q.order_by(WechatArticle.created_at.desc())
                      .offset((page-1)*size).limit(size).all())
        result = {
            "total": total,
            "page": page,
            "size": size,
            "data": [
                {
                    "id": x.id,
                    "title": x.title,
                    "author": x.author,
                    "tag": x.tag,
                    "created_at": x.created_at
                } for x in rows
            ]
        }
        logger.info(f"Successfully fetched {len(rows)} articles out of {total} total")
        return result
    except Exception as e:
        logger.error(f"Error in list_articles: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/articles/{aid}")
async def get_article(aid: int):
    try:
        logger.info(f"Fetching article with ID: {aid}")
        with SessionLocal() as s:
            art = s.get(WechatArticle, aid)
            if not art:
                logger.warning(f"Article with ID {aid} not found")
                raise HTTPException(404, "not found")
            result = {
                "id": art.id,
                "url": art.url,
                "title": art.title,
                "author": art.author,
                "published_at": art.published_at,
                "cover_image": art.cover_image,
                "content_html": art.content_html,
                "content_text": art.content_text,
                "tag": art.tag
            }
            logger.info(f"Successfully fetched article: {art.title}")
            return result
    except Exception as e:
        logger.error(f"Error in get_article: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")
