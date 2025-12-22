<template>
  <article class="card" @click="goDetail">
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

const router = useRouter()

const profileSrc = computed(() => {
  const p = props.person.profile_path
  if (!p) return ''
  return `https://image.tmdb.org/t/p/w500${p}`
})

function goDetail() {
  if (props.person.tmdb_id) {
    router.push({ name: 'person-detail', params: { tmdbId: props.person.tmdb_id } })
  }
}
</script>

<style scoped>
.card { width: 120px; cursor: pointer; user-select: none; }
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