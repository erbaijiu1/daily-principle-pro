from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from db import Base, engine, SessionLocal
from models import WechatArticle
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import requests
from lxml import html, etree
from readability import Document
from datetime import datetime

app = FastAPI(title="Daily Principle Archiver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

class CrawlReq(BaseModel):
    url: HttpUrl
    tag: Optional[str] = "每日原则"

def extract_with_readability(page_html: str):
    doc = Document(page_html)
    title = doc.short_title()
    content_html = doc.summary(html_partial=True)
    tree = html.fromstring(content_html)
    text = " ".join(tree.xpath("string(.)").split())
    return title, content_html, text

def parse_wechat_article(page_html: str):
    tree = html.fromstring(page_html)

    title = tree.xpath('string(//*[@id="activity-name"] | //h1[contains(@class,"rich_media_title")] | //h1)').strip()
    author = tree.xpath('string(//*[@id="js_name"] | //*[@class="rich_media_meta rich_media_meta_text"] | //*[@class="profile_nickname"])').strip()
    content_nodes = tree.xpath('//*[@id="js_content"]')

    if content_nodes:
        content_el = content_nodes[0]
        content_el.attrib.pop("style", None)
        content_html = etree.tostring(content_el, method="html", encoding="unicode")
        content_text = " ".join(content_el.xpath("string(.)").split())
    else:
        _t, content_html, content_text = extract_with_readability(page_html)
        if not title: title = _t

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
        title = t2 or "未命名文章"

    return title, author, published_at, cover, content_html, content_text

@app.post("/crawl/wechat")
def crawl_wechat(req: CrawlReq):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Referer": "https://mp.weixin.qq.com/"
    }
    r = requests.get(str(req.url), headers=headers, timeout=20)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"fetch failed: {r.status_code}")

    title, author, published_at, cover, content_html, content_text = parse_wechat_article(r.text)

    with SessionLocal() as s:
        art = WechatArticle(
            url=str(req.url), title=title, author=author,
            published_at=published_at, cover_image=cover,
            content_html=content_html, content_text=content_text,
            tag=req.tag or "每日原则"
        )
        s.add(art)
        try:
            s.commit(); s.refresh(art)
        except IntegrityError:
            s.rollback()
            art = s.execute(select(WechatArticle).where(WechatArticle.url == str(req.url))).scalar_one()
    return {"id": art.id, "title": art.title, "author": art.author, "tag": art.tag}

@app.get("/articles")
def list_articles(tag: Optional[str] = Query(None), page: int = 1, size: int = 10):
    page = max(page,1); size = max(min(size,50),1)
    with SessionLocal() as s:
        q = s.query(WechatArticle)
        if tag: q = q.filter(WechatArticle.tag == tag)
        total = q.count()
        rows = (q.order_by(WechatArticle.created_at.desc())
                  .offset((page-1)*size).limit(size).all())
    return {"total": total, "page": page, "size": size,
            "data":[{"id":x.id,"title":x.title,"author":x.author,"tag":x.tag,"created_at":x.created_at} for x in rows]}

@app.get("/articles/{aid}")
def get_article(aid: int):
    with SessionLocal() as s:
        art = s.get(WechatArticle, aid)
        if not art: raise HTTPException(404, "not found")
        return {"id": art.id, "url": art.url, "title": art.title, "author": art.author,
                "published_at": art.published_at, "cover_image": art.cover_image,
                "content_html": art.content_html, "content_text": art.content_text, "tag": art.tag}
