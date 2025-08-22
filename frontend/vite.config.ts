import { defineConfig } from 'vite'
import { resolve } from 'path'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  base: process.env.NODE_ENV === 'production' ? '/daily_static/' : '/daily_static',
  resolve: { alias: { '@': resolve(__dirname, './') } },
  // （可选）开发期想用同域路径，可在这里配代理，把 /daily_principle 转到后端
  // server: {
  //   proxy: {
  //     '/daily_principle': {
  //       target: 'http://localhost:8089/daily_principle',
  //       changeOrigin: true
  //     }
  //   }
  // }
})
