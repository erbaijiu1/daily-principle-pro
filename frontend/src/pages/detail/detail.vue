<template>
  <scroll-view scroll-y class="container">
    <view class="title">{{ article.title }}</view>
    <view class="meta">{{ article.author }} {{ article.published_at || '' }}</view>
    <rich-text :nodes="article.content_html"></rich-text>
  </scroll-view>
</template>

<script>
export default {
  data(){ return { article:{} } },
  onLoad(q){ this.load(q.id) },
  methods:{
    load(id){
      uni.request({
        url: `/daily_principle/articles/${id}`,
        success: (res)=> this.article = res.data || {}
      })
    }
  }
}
</script>

<style>
.container{ padding:24rpx; }
.title{ font-size:40rpx; font-weight:800; margin-bottom:12rpx; }
.meta{ color:#888; margin-bottom:20rpx; }
</style>
