<template>
  <article class="card" @click="goDetail">
    <button class="heart-badge" @click.stop="onUnlike">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="#ff2f6e">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
    </button>

    <div class="poster-wrap">
      <img v-if="profileSrc" :src="profileSrc" class="poster" alt="profile" />
      <div v-else class="poster-fallback">No Image</div>
    </div>
    <div class="meta">
      <p class="name">{{ person.name }}</p>
      <p class="dept">{{ person.known_for_department }}</p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  person: { type: Object, required: true }
})

const emit = defineEmits(['toggle-like']) // ✅ 이벤트 정의 추가
const router = useRouter()

const profileSrc = computed(() => {
  const p = props.person.profile_path
  if (!p) return ''
  return `https://image.tmdb.org/t/p/w500${p}` // w185 -> w500 (화질 개선)
})

function goDetail() {
  if (props.person.tmdb_id) {
    router.push({ name: 'person-detail', params: { tmdbId: props.person.tmdb_id } })
  }
}

// ✅ 좋아요 취소 핸들러
function onUnlike() {
  emit('toggle-like', props.person)
}
</script>

<style scoped>
.card { 
  width: 120px; cursor: pointer; user-select: none; 
  position: relative; /* ✅ 하트 버튼 기준점 */
}

/* ✅ 하트 버튼 스타일 추가 */
.heart-badge {
  position: absolute; top: 6px; right: 6px; z-index: 5;
  width: 26px; height: 26px;
  background: rgba(255, 255, 255, 0.9); /* 살짝 투명한 흰색 배경 */
  border: 1px solid #eee; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  padding: 0;
}
.heart-badge:hover { transform: scale(1.1); }

.poster-wrap {
  width: 120px; height: 180px; /* 2:3 비율 */
  border-radius: 12px; overflow: hidden; background: #f2f2f2;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.poster { width: 100%; height: 100%; object-fit: cover; }
.poster-fallback { width: 100%; height: 100%; display: grid; place-items: center; color: #777; font-size: 12px; }
.meta { margin-top: 8px; text-align: center; }
.name { font-size: 13px; font-weight: 700; margin: 0; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dept { font-size: 11px; color: var(--muted); margin: 2px 0 0; }
</style>