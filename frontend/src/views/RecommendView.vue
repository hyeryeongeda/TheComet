<!-- frontend/src/views/RecommendView.vue -->
<template>
  <main class="page">
    <section class="container">
      <h1 class="title">추천</h1>

      <!-- 탭 -->
      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'chat' }" @click="tab = 'chat'">AI 맞춤</button>
        <button class="tab" :class="{ active: tab === 'genre' }" @click="tab = 'genre'">장르</button>
        <button class="tab" :class="{ active: tab === 'person' }" @click="tab = 'person'">인물</button>
        <button class="tab" :class="{ active: tab === 'user' }" @click="tab = 'user'">유저</button>
      </div>

      <!-- AI 탭 -->
      <div v-if="tab === 'chat'" class="panel">
        <div class="chat-box">
          <div v-for="(m, idx) in chatMessages" :key="idx" class="msg" :class="m.role">
            <span class="bubble">{{ m.content }}</span>
          </div>
          <div v-if="chatLoading" class="msg assistant">
            <span class="bubble">추천 생성 중...</span>
          </div>
        </div>

        <form class="input-row" @submit.prevent="sendChat">
          <input
            v-model="chatInput"
            class="input"
            placeholder="예) 기분 전환되는 코미디 + 러닝타임 짧은 걸로 추천해줘"
          />
          <button class="btn" type="submit" :disabled="chatLoading || !chatInput.trim()">보내기</button>
        </form>

        <!-- ✅ 추천 영화 카드 (목업처럼 세로 리스트) -->
        <div v-if="chatMovies.length" class="rec-list">
          <button
            v-for="m in chatMovies.slice(0, 3)"
            :key="movieId(m)"
            class="rec-card"
            type="button"
            @click="goMovie(m)"
          >
            <div class="rec-thumb">
              <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="" />
              <div v-else class="noimg">No Image</div>
            </div>

            <div class="rec-body">
              <p class="rec-title">{{ m.title }}</p>
              <p class="rec-meta">
                ★ {{ Number(m.vote_average || 0).toFixed(1) }}
                <span v-if="m.release_date"> · {{ m.release_date.slice(0, 4) }}</span>
              </p>
              <p class="rec-genres" v-if="m.genres?.length">{{ genreLine(m) }}</p>
            </div>
          </button>
        </div>

        <div v-else-if="askedOnce && !chatLoading" class="empty-movies">
          추천 영화가 아직 없어요.
        </div>
      </div>

      <!-- 장르 탭 -->
      <div v-else-if="tab === 'genre'" class="panel">
        <div class="head-row">
          <p class="sub">내 활동 기반 장르 추천</p>
          <button class="ghost" @click="loadGenre" :disabled="loading.genre">새로고침</button>
        </div>

        <div v-if="loading.genre" class="loading">로딩중...</div>
        <div v-else class="grid">
          <div v-for="(g, idx) in genreItems" :key="idx" class="card">
            <p class="card-title">{{ g.name || g.genre_name || g.title || 'Genre' }}</p>
            <p class="card-desc">{{ g.reason || g.description || '' }}</p>
          </div>
        </div>
      </div>

      <!-- 인물 탭 -->
      <div v-else-if="tab === 'person'" class="panel">
        <div class="head-row">
          <p class="sub">내 활동 기반 인물 추천</p>
          <button class="ghost" @click="loadPerson" :disabled="loading.person">새로고침</button>
        </div>

        <div v-if="loading.person" class="loading">로딩중...</div>
        <div v-else class="grid">
          <div v-for="(p, idx) in personItems" :key="idx" class="card">
            <p class="card-title">{{ p.name || p.person_name || 'Person' }}</p>
            <p class="card-desc">{{ p.reason || p.description || '' }}</p>
          </div>
        </div>
      </div>

      <!-- 유저 탭 -->
      <div v-else class="panel">
        <div class="head-row">
          <p class="sub">취향이 비슷한 유저 추천</p>
          <button class="ghost" @click="loadUser" :disabled="loading.user">새로고침</button>
        </div>

        <div v-if="loading.user" class="loading">로딩중...</div>
        <div v-else class="grid">
          <div v-for="(u, idx) in userItems" :key="idx" class="card">
            <p class="card-title">@{{ u.username || u.name || 'user' }}</p>
            <p class="card-desc">{{ u.reason || u.bio || '' }}</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  postTasteChat,
  fetchGenreRecommends,
  fetchPersonRecommends,
  fetchUserRecommends,
} from '@/api/comet'

const router = useRouter()
const tab = ref('chat')

// --- AI 챗봇 탭 ---
const chatMessages = ref([
  { role: 'assistant', content: '원하는 분위기/장르/제외조건을 말해주면 맞춤 추천해줄게요.' },
])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMovies = ref([])
const askedOnce = ref(false)

function posterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w342${path}` : ''
}

function movieId(m) {
  return m?.tmdb_id ?? m?.tmdbId ?? m?.id
}

function genreLine(m) {
  return (m?.genres ?? []).map((g) => g.name).join(' · ')
}

function goMovie(m) {
  const id = movieId(m)
  if (!id) return
  router.push({ name: 'movie-detail', params: { tmdbId: id } })
}

function pickMovies(res) {
  // ✅ 어떤 래핑이 와도 movies를 최대한 찾아서 배열로 맞춤
  const movies =
    res?.movies ??
    res?.results ??
    res?.data?.movies ??
    res?.data?.results ??
    []
  return Array.isArray(movies) ? movies : []
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  askedOnce.value = true
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true

  try {
    const history = chatMessages.value.map((m) => ({ role: m.role, content: m.content }))
    const res = await postTasteChat({ message: text, history })

    // ✅ 백 응답 기준: answer, movies (혹시 reply로 오면 fallback)
    const reply = res?.answer || res?.reply || '응답이 비어있어요.'
    chatMessages.value.push({ role: 'assistant', content: reply })

    // ✅ 영화 카드용 데이터 저장(키 방어)
    chatMovies.value = pickMovies(res)

    // 디버그 필요하면 주석 해제
    // console.log('AI res:', res)
    // console.log('AI movies:', chatMovies.value.length, chatMovies.value[0])
  } catch (e) {
    console.error(e)
    chatMessages.value.push({ role: 'assistant', content: '에러가 발생했어요. 다시 시도해 주세요.' })
    chatMovies.value = []
  } finally {
    chatLoading.value = false
  }
}

// --- 추천 탭 데이터 ---
const loading = ref({ genre: false, person: false, user: false })
const genreItems = ref([])
const personItems = ref([])
const userItems = ref([])

function normalizeList(res) {
  if (Array.isArray(res)) return res
  if (Array.isArray(res?.results)) return res.results
  if (Array.isArray(res?.data)) return res.data
  return []
}

async function loadGenre() {
  loading.value.genre = true
  try {
    const res = await fetchGenreRecommends()
    genreItems.value = normalizeList(res)
  } finally {
    loading.value.genre = false
  }
}

async function loadPerson() {
  loading.value.person = true
  try {
    const res = await fetchPersonRecommends()
    personItems.value = normalizeList(res)
  } finally {
    loading.value.person = false
  }
}

async function loadUser() {
  loading.value.user = true
  try {
    const res = await fetchUserRecommends()
    userItems.value = normalizeList(res)
  } finally {
    loading.value.user = false
  }
}

// 탭 바뀔 때 최초 1회 로드
watch(
  () => tab.value,
  (t) => {
    if (t === 'genre' && genreItems.value.length === 0) loadGenre()
    if (t === 'person' && personItems.value.length === 0) loadPerson()
    if (t === 'user' && userItems.value.length === 0) loadUser()
  },
  { immediate: true },
)
</script>

<style scoped>
.page { min-height: calc(100vh - 60px); background: #fff; }
.container { width: min(1000px, 92vw); margin: 0 auto; padding: 22px 0 60px; }
.title { margin: 0 0 14px; font-size: 26px; font-weight: 900; }

.tabs { display: flex; gap: 8px; margin-bottom: 14px; }
.tab {
  height: 38px; padding: 0 12px; border-radius: 12px;
  border: 1px solid #e6e6e6; background: #fff;
  font-weight: 900; cursor: pointer;
}
.tab.active { border-color: #111; background: #111; color: #fff; }

.panel { border: 1px solid #eee; border-radius: 16px; padding: 14px; background: #fff; }

.chat-box {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 14px;
  background: #fafafa;
  min-height: 320px;
  display: grid;
  gap: 10px;
}
.msg { display: flex; }
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }
.bubble {
  max-width: 78%;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid #eaeaea;
  background: #fff;
  font-weight: 700;
  line-height: 1.45;
  color: #222;
}
.msg.user .bubble { background: #111; color: #fff; border-color: #111; }

.input-row {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 100px;
  gap: 10px;
}
.input {
  height: 44px;
  border-radius: 12px;
  border: 1px solid #ddd;
  padding: 0 12px;
  font-weight: 700;
}
.btn {
  height: 44px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.head-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sub { margin: 0; font-weight: 900; color: #111; }
.ghost {
  height: 34px; padding: 0 10px; border-radius: 12px;
  border: 1px solid #ddd; background: #fff; font-weight: 900; cursor: pointer;
}
.ghost:disabled { opacity: 0.5; cursor: not-allowed; }

.loading { padding: 10px 0; font-weight: 800; color: #666; }

.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
@media (max-width: 900px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }

.card {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 12px;
  background: #fafafa;
}
.card-title { margin: 0 0 6px; font-weight: 900; }
.card-desc { margin: 0; color: #444; font-weight: 700; line-height: 1.4; }

/* ✅ AI 추천 카드(목업 느낌: 세로 3개 카드) */
.rec-list{
  margin-top: 14px;
  display: grid;
  gap: 12px;
}
.rec-card{
  width: 100%;
  border: 1px solid #eee;
  border-radius: 16px;
  background: #fff;
  padding: 12px;
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 12px;
  text-align: left;
  cursor: pointer;
}
.rec-thumb{
  width: 110px;
  aspect-ratio: 2/3;
  border-radius: 12px;
  overflow: hidden;
  background: #f2f2f2;
  display: grid;
  place-items: center;
}
.rec-thumb img{ width:100%; height:100%; object-fit: cover; }
.noimg{ color:#777; font-weight: 800; }

.rec-body{ display: grid; align-content: start; gap: 6px; }
.rec-title{ margin:0; font-weight: 900; font-size: 16px; }
.rec-meta{ margin:0; color:#666; font-weight: 800; font-size: 13px; }
.rec-genres{ margin:0; color:#333; font-weight: 800; font-size: 13px; }

.empty-movies{ margin-top: 14px; color:#777; font-weight: 800; }
</style>
