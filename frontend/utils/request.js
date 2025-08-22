// utils/request.js
import { buildUrl } from '@/config/env.ts';

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

function request(method, path, data = {}, options = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: buildUrl(path),
      method,
      data,
      header: { ...DEFAULT_HEADERS, ...(options.header || {}) },
      timeout: options.timeout || 15000,
      success: (res) => {
        // 这里可按你的后端返回格式统一处理
        resolve(res.data);
      },
      fail: (err) => reject(err),
    });
  });
}

export const http = {
  get: (path, params, opt) => request('GET', path, params, opt),
  post: (path, body, opt) => request('POST', path, body, opt),
  put: (path, body, opt) => request('PUT', path, body, opt),
  del: (path, body, opt) => request('DELETE', path, body, opt),
};
