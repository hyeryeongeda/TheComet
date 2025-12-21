<template>
  <main class="page">
    <div class="container">
      <div v-if="loading">로딩중...</div>
      <div v-else-if="!person">인물 정보를 불러오지 못했습니다.</div>

      <div v-else>
        <section class="hero">
          <img v-if="profileSrc" class="avatar" :src="profileSrc" />
          <div v-else class="avatar fallback">No Image</div>

          <div class="meta">
            <h1 class="name">{{ person.name }}</h1>
            <p class="dept">{{ person.known_for_department || 'Person' }}</p>

            <div class="tabs">
              <button :class="{active: tab==='cast'}" @click="tab='cast'">출연</button>
              <button :class="{active: tab==='directors'}" @click="tab='directors'">감독</button>
            </div>
          </div>
        </section>

        <section v-if="tab==='cast'">
          <h2 class="h2">출연작</h2>
          <div class="grid">
            <div v-for="m in person.cast" :key="m.movie_tmdb_id" class="card" @click="goMovie(m.movie_tmdb_id)">
              <img v-if="m.poster_path" class="poster" :src="poster(m.poster_path)" />
              <div v-else class="poster fallback">No</div>
              <div class="title">{{ m.movie_title }}</div>
              <div class="sub" v-if="m.character_name">{{ m.character_name }}</div>
            </div>
          </div>
        </section>

        <section v-else>
          <h2 class="h2">감독작</h2>
          <div class="grid">
            <div v-for="m in person.directors" :key="m.movie_tmdb_id" class="card" @click="goMovie(m.movie_tmdb_id)">
              <img v-if="m.poster_path" class="poster" :src="poster(m.poster_path)" />
              <div v-else class="poster fallback">No</div>
              <div class="title">{{ m.movie_title }}</div>
              <div class="sub" v-if="m.job">{{ m.job }}</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPersonDetail } from '@/api/comet'

const route = useRoute()
const router = useRouter()

const tmdbId = computed(() => Number(route.params.tmdbId))
const loading = ref(true)
const person = ref(null)
const tab = ref('cast')

const profileSrc = computed(() => {
  const p = person.value?.profile_path
  return p ? `https://image.tmdb.org/t/p/w300${p}` : ''
})

const poster = (path) => `https://image.tmdb.org/t/p/w342${path}`

async function load() {
  loading.value = true
  try {
    person.value = await fetchPersonDetail(tmdbId.value)
    tab.value = (person.value?.cast?.length ?? 0) > 0 ? 'cast' : 'directors'
  } catch (e) {
    console.error(e)
    person.value = null
  } finally {
    loading.value = false
  }
}

function goMovie(id) {
  router.push({ name: 'movie-detail', params: { tmdbId: id } })
}

onMounted(load)
watch(tmdbId, load)
</script>

<style scoped>
.page { background:#fff; min-height:calc(100vh - 60px); }
.container { width:min(1100px, 92vw); margin:0 auto; padding:22px 0 60px; }

.hero { display:flex; gap:16px; align-items:center; margin-bottom:18px; }
.avatar { width:88px; height:88px; border-radius:18px; object-fit:cover; background:#f2f2f2; }
.fallback { display:grid; place-items:center; color:#777; }

.name { margin:0; font-size:28px; font-weight:900; }
.dept { margin:6px 0 0; color:#666; font-weight:700; }

.tabs { display:flex; gap:10px; margin-top:12px; }
.tabs button { height:36px; padding:0 14px; border-radius:999px; border:1px solid #ddd; background:#fff; font-weight:800; cursor:pointer; }
.tabs button.active { border-color:#111; }

.h2 { margin:16px 0 10px; font-size:18px; font-weight:900; }
.grid { display:grid; grid-template-columns:repeat(6, 1fr); gap:12px; }
.card { cursor:pointer; border:1px solid #eee; border-radius:14px; overflow:hidden; background:#fff; }
.poster { width:100%; aspect-ratio:2/3; object-fit:cover; background:#f2f2f2; }
.title { padding:10px 10px 0; font-weight:900; font-size:13px; }
.sub { padding:6px 10px 10px; color:#666; font-weight:700; font-size:12px; }

@media (max-width: 980px){ .grid{ grid-template-columns:repeat(4, 1fr);} }
@media (max-width: 640px){ .grid{ grid-template-columns:repeat(2, 1fr);} }
</style>
