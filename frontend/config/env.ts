// config/env.js
// 统一管理 API 前缀与 URL 拼接
export const API_BASE =
  (import.meta.env && import.meta.env.VITE_API_BASE) || '/daily_principle';

// 规范化：确保只有一个斜杠
export const buildUrl = (path = '') =>
  `${API_BASE.replace(/\/$/, '')}/${String(path).replace(/^\//, '')}`;

// 可选：集中管理常用接口路径
export const API = {
  articles: '/articles',
  crawl: '/crawl/wechat',
};
