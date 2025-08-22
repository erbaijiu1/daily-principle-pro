<template>
  <scroll-view scroll-y class="container">
    <view v-if="article" class="article selectable">
      <view class="title">{{ article.title }}</view>
      <view class="meta">
        {{ article.author || '佚名' }} · {{ formatDate(article.published_at || article.created_at) }}
      </view>

      <!-- 外面包一层，给正文区独立样式 -->
      <view class="rich-wrap">
        <rich-text :nodes="article.content_html"></rich-text>
      </view>
    </view>

    <view v-else class="loading">加载中…</view>
  </scroll-view>
</template>

<script>
import { http } from '@/utils/request.js'
import { API } from '@/config/env.ts'

export default {
  data(){ return { article: null, loading: false } },
  onLoad(q){
    const id = q && q.id
    if (!id) return uni.showToast({ title: '缺少文章ID', icon: 'none' })
    this.load(id)
  },
  methods:{
    async load(id){
      this.loading = true
      try {
        const res = await http.get(`${API.articles}/${id}`)
        this.article = res || {}
      } finally { this.loading = false }
    },
    formatDate(ts){
      if(!ts) return ''
      let s = String(ts).replace('T',' ').replace('Z','')
      const d = new Date(s.replace(/-/g,'/'))
      if (isNaN(d)) return ts
      const pad = n => (n<10? '0'+n : ''+n)
      return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
    }
  }
}
</script>

<style>
/* 页面整体内边距 */
.container{ padding: 16px; box-sizing: border-box; }

/* 正文区域：限制最大宽度并居中（PC 不会铺太宽，移动端占满） */
.article{ max-width: 820px; margin: 0 auto; }

/* 标题/副标题 */
.title{ font-size: 40rpx; font-weight: 800; margin-bottom: 12rpx; }
.meta{ color:#888; margin-bottom: 20rpx; }
.loading{ color:#888; padding: 24rpx; }

/* -------- 让正文可以被选中（只作用于正文区） -------- */
.selectable, .selectable *{
  -webkit-user-select: text !important;
  user-select: text !important;
}

/* -------- rich-text 内常见元素的基础排版 -------- */
.rich-wrap{ line-height: 1.9; font-size: 16px; }
.rich-wrap :deep(p){ margin: 0 0 1em; text-align: justify; }
.rich-wrap :deep(img){
  max-width: 100% !important;
  height: auto !important;
  display: block;
  margin: 8px auto;
}
.rich-wrap :deep(section), 
.rich-wrap :deep(div){
  /* 处理公众号里常见的内联 margin/padding 导致的空白 */
  box-sizing: border-box;
}
</style>
