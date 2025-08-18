# Daily Principle 存档模板

一键启动：FastAPI + MySQL + uni-app(H5) + Nginx 反代。

## 快速开始
```bash
cp .env.example .env
docker compose up -d --build
```

前端访问：`http://localhost:8080`  
粘贴文章链接（如某篇“每日原则”的 mp.weixin 链接）点击“抓取并入库”。

也可直接用 API：
```bash
curl -X POST "http://localhost:8080/api/crawl/wechat"   -H "Content-Type: application/json"   -d '{"url":"https://mp.weixin.qq.com/s/mWZl9DYsXP5cp4-LwaUScQ","tag":"每日原则"}'
```

## 目录
- `server/` FastAPI 服务（抓取、列表、详情）
- `frontend/` uni-app H5（两页：列表/详情）
- `sql/init.sql` 初始化表结构

## 备注
- 默认仅打包 H5；若要小程序/APP，请在本地用 HBuilderX/CLI 构建相应平台。
- 若需要图片本地化、全文检索或登录鉴权，可在此模板基础上继续扩展。
