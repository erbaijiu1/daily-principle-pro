<template>
  <view class="container">
    <view class="title">每日原则 · 文章列表</view>
    <view v-for="item in list" :key="item.id" class="card" @tap="go(item.id)">
      <view class="h">{{ item.title }}</view>
      <view class="sub">{{ item.author || '佚名' }} · {{ item.created_at }}</view>
    </view>

    <view class="actions">
      <input class="input" v-model="url" placeholder="粘贴文章链接" />
      <button class="btn" @tap="crawl">抓取并入库</button>
    </view>
  </view>
</template>

<script>
export default {
  data(){ return { list: [], url: '' } },
  onLoad(){ this.fetch() },
  methods:{
    apiBase(){ return '/api' },
    fetch(){
      uni.request({
        url: this.apiBase() + '/articles?tag=每日原则&page=1&size=20',
        success: (res)=> this.list = res.data?.data || []
      })
    },
    go(id){ uni.navigateTo({ url: `/pages/detail/detail?id=${id}` }) },
    crawl(){
      if(!this.url) return uni.showToast({title:'请粘贴链接', icon:'none'})
      uni.request({
        url: this.apiBase() + '/crawl/wechat',
        method:'POST',
        data:{ url: this.url, tag:'每日原则' },
        success: ()=>{ uni.showToast({title:'已入库'}); this.fetch(); },
        fail: ()=> uni.showToast({title:'失败', icon:'none'})
      })
    }
  }
}
</script>

<style>
.container{ padding:24rpx; }
.title{ font-size:36rpx; font-weight:700; margin-bottom:24rpx; }
.card{ padding:24rpx; background:#fff; border-radius:16rpx; margin-bottom:20rpx; box-shadow:0 2rpx 12rpx rgba(0,0,0,.04); }
.h{ font-size:32rpx; line-height:1.4; }
.sub{ color:#888; margin-top:8rpx; font-size:24rpx; }
.actions{ margin-top:24rpx; display:flex; gap:12rpx; }
.input{ flex:1; background:#fff; border:1px solid #ddd; border-radius:12rpx; padding:16rpx; }
.btn{ background:#3b82f6; color:#fff; border-radius:12rpx; padding:0 24rpx; height:72rpx; line-height:72rpx; }
</style>
