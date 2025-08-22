<template>
  <view class="container">
    <view class="title">每日原则 · 文章列表</view>

    <!-- 用 <navigator> 跳详情，跨端稳定 -->
    <navigator
      v-for="item in list"
      :key="item.id"
      :url="`/pages/detail/detail?id=${item.id}`"
      hover-class="none"
      class="card"
    >
      <view class="h">{{ item.title }}</view>
      <view class="sub">{{ item.author || '佚名' }} · {{ item.created_at }}</view>
    </navigator>

  <view class="actions">
    <input class="input" v-model="url" placeholder="粘贴文章链接" />
    <button class="btn" :disabled="loading" @click="crawl">
      {{ loading ? '处理中...' : '抓取并入库' }}
    </button>
  </view>
  </view>
</template>

<script>
import { http } from '@/utils/request.js';
import { API } from '@/config/env.ts';

export default {
  data(){ return { list: [], url: '', loading: false } },
  onLoad(){ this.fetch() },
  methods:{
    async fetch(){
      try {
        const res = await http.get(API.articles, { tag:'principle', page:1, size:20 });
        this.list = res?.data || [];
      } catch (e) {
        uni.showToast({ title: '列表请求失败', icon: 'none' })
      }
    },
    async crawl(){
      const link = (this.url || '').trim();
      if(!link) return uni.showToast({title:'请粘贴链接', icon:'none'});

      this.loading = true;
      try {
        const resp = await http.post(API.crawl, { url: link, tag:'principle' });
        // 成功：清空输入框
        this.url = '';
        // 根据是否重复给提示
        if (resp?.skipped) {
          uni.showToast({ title: '已存在（未重复入库）', icon: 'none' });
        } else {
          uni.showToast({ title: '已入库' });
        }
        this.fetch();
      } catch (e) {
        uni.showToast({title:'抓取失败', icon:'none'});
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>


<style scoped>
.container{ padding:24rpx; }
.title{ font-size:36rpx; font-weight:700; margin-bottom:24rpx; }
.card{ padding:24rpx; background:#fff; border-radius:16rpx; margin-bottom:20rpx; box-shadow:0 2rpx 12rpx rgba(0,0,0,.04); display:block; text-decoration:none; color:inherit; }
.h{ font-size:32rpx; line-height:1.4; }
.sub{ color:#888; margin-top:8rpx; font-size:24rpx; }
.actions{ margin-top:24rpx; display:flex; gap:12rpx; }
.input{ flex:1; background:#fff; border:1px solid #ddd; border-radius:12rpx; padding:16rpx; }
.btn{ background:#3b82f6; color:#fff; border-radius:12rpx; padding:0 24rpx; height:72rpx; line-height:72rpx; }
.btn[disabled]{ opacity:.5; filter: grayscale(0.2); }

</style>
