<template>
  <section class="sub-section">
    <h3 class="sub-title">출연/제작</h3>
    <div class="scroll-wrapper">
      <button class="circle-arrow-btn left" @click="scrollCast(-1)">‹</button>
      <div ref="castRail" class="horizontal-scroll">
        <div v-for="p in allCast" :key="p.tmdb_id" class="cast-card" @click="$emit('go-person', p.tmdb_id)">
          <div class="cast-img-box">
            <img v-if="p.profile_path" :src="`https://image.tmdb.org/t/p/w200${p.profile_path}`" />
            <div v-else class="no-img">👤</div>
          </div>
          <div class="cast-text">
            <div class="c-name">{{ p.name }}</div>
            <div class="c-role">{{ p.role_desc }}</div>
          </div>
        </div>
      </div>
      <button class="circle-arrow-btn right" @click="scrollCast(1)">›</button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
defineProps(['allCast'])
defineEmits(['go-person'])

const castRail = ref(null)
function scrollCast(dir) {
  if (castRail.value) castRail.value.scrollBy({ left: dir * 300, behavior: 'smooth' })
}
</script>

<style scoped>
/* 관련 스타일 복사 (.scroll-wrapper, .cast-card 등) */
.sub-title { font-size: 20px; font-weight: 800; margin-bottom: 20px; }
.scroll-wrapper { position: relative; }
.horizontal-scroll { display: flex; gap: 14px; overflow-x: auto; scrollbar-width: none; }
.horizontal-scroll::-webkit-scrollbar { display: none; }
.cast-card { width: 110px; flex-shrink: 0; cursor: pointer; transition: transform 0.2s; }
.cast-card:hover { transform: scale(1.05); }
.cast-img-box { width: 110px; height: 110px; border-radius: 6px; overflow: hidden; background: #f8f8f8; border: 1px solid #eee; margin-bottom: 8px; }
.cast-img-box img { width: 100%; height: 100%; object-fit: cover; }
.c-name { font-size: 13px; font-weight: 600; }
.c-role { font-size: 12px; color: #888; }
.circle-arrow-btn { position: absolute; top: 35px; width: 36px; height: 36px; border-radius: 50%; background: white; border: 1px solid #ddd; z-index: 10; cursor: pointer; }
.circle-arrow-btn.left { left: -15px; }
.circle-arrow-btn.right { right: -15px; }
</style>