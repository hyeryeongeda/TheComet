<template>
  <main class="page">
    <div v-if="loading" class="loading-screen">로딩중...</div>
    <div v-else-if="!movie" class="error-screen">영화를 불러오지 못했습니다.</div>

    <div v-else>
      <MovieHero :movie="movie" />

      <div class="container body-wrapper">
        <div class="top-section">
          <div class="poster-area">
            <div class="poster-card">
              <img v-if="posterSrc" :src="posterSrc" class="poster-img" alt="poster" />
              <div v-else class="poster-fallback">No Image</div>
            </div>
          </div>

          <MovieActionRow 
            :isLiked="isLiked" 
            :isWished="isWished"
            :starWidth="starWidth"
            :voteScore="voteScore"
            :voteCount="movie.vote_count"
            @toggle-like="onToggleLike"
            @toggle-wish="onToggleWish"
            @open-write-modal="openWriteModal"
          />
        </div>

        <p class="overview">{{ movie.overview || '등록된 줄거리가 없습니다.' }}</p>

        <div class="section-divider"></div>

        <MovieCastRail :allCast="allCast" @go-person="goPerson" />

        <div class="section-divider"></div>

        <MovieCommentSection 
          :reviews="reviews" 
          @open-list-modal="openListModal"
          @open-detail-modal="openDetailModal"
        />

        <div class="section-divider"></div>

        <section class="sub-section">
          <h3 class="sub-title">비슷한 작품</h3>
          <MovieRow v-if="similarList.length > 0" title="" :movies="similarList" />
          <div v-else class="no-data">관련 영화 정보를 불러오는 중입니다...</div>
        </section>
      </div>
    </div>

    <ReviewWriteModal 
      v-if="showWriteModal"
      :movieTitle="movie ? movie.title : ''"
      :existingReview="myReview"
      @close="showWriteModal = false"
      @submit="handleWriteSubmit"
      @delete="handleWriteDelete"
    />

    <ReviewListModal
      v-if="showListModal"
      :reviews="reviews"
      @close="showListModal = false"
      @sort="handleSort"
      @select="openDetailModal"
    />

    <ReviewDetailModal
      v-if="showDetailModal && selectedReview"
      :review="selectedReview"
      :replies="reviewComments"
      @close="showDetailModal = false"
      @submit-reply="handleReplySubmit"
      @toggle-like="handleReviewLike"
      @delete-reply="handleReplyDelete"
    />
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  fetchMovieDetail, fetchMovieReviews, fetchSimilarMovies, fetchMovies, 
  toggleMovieLike, fetchMyLikes, createMovieReview, fetchReviewComments,
  createReviewComment, fetchMyActivity, toggleReviewLike, toggleMovieWish,
  deleteReview, updateReview, fetchMyReview
} from '@/api/comet'

// 공통 컴포넌트
import MovieRow from '@/components/movie/MovieRow.vue'

// 분리한 상세 컴포넌트들
import MovieHero from '@/components/moviedetail/MovieHero.vue'
import MovieActionRow from '@/components/moviedetail/MovieActionRow.vue'
import MovieCastRail from '@/components/moviedetail/MovieCastRail.vue'
import MovieCommentSection from '@/components/moviedetail/MovieCommentSection.vue'

// 모달 컴포넌트
import ReviewWriteModal from '@/components/review/ReviewWriteModal.vue'
import ReviewListModal from '@/components/review/ReviewListModal.vue'
import ReviewDetailModal from '@/components/review/ReviewDetailModal.vue'

// 기본 설정
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tmdbId = computed(() => route.params.tmdbId)

// 상태 변수
const loading = ref(true)
const movie = ref(null)
const reviews = ref([])
const similarList = ref([])
const isLiked = ref(false)
const isWished = ref(false)
const myReview = ref(null)

// 모달 상태
const showWriteModal = ref(false)
const showListModal = ref(false)
const showDetailModal = ref(false)
const selectedReview = ref(null)
const reviewComments = ref([])

// === Computed 데이터 처리 ===
const posterSrc = computed(() => movie.value?.poster_path ? `https://image.tmdb.org/t/p/w500${movie.value.poster_path}` : '')
const voteScore = computed(() => movie.value?.vote_average ? Number(movie.value.vote_average).toFixed(1) : '0.0')
const starWidth = computed(() => `${(movie.value?.vote_average || 0) * 10}%`)
const allCast = computed(() => {
  if (!movie.value) return []
  const dirs = (movie.value.directors || []).map(p => ({ ...p, role_desc: '감독' }))
  const acts = (movie.value.cast || []).map(p => ({ ...p, role_desc: '출연' }))
  return [...dirs, ...acts]
})

// === 데이터 로드 로직 ===
async function loadAll() {
  loading.value = true
  isLiked.value = false
  isWished.value = false
  myReview.value = null

  try {
    const id = Number(tmdbId.value)
    const [m, r] = await Promise.all([fetchMovieDetail(id), fetchMovieReviews(id)])
    movie.value = m
    reviews.value = Array.isArray(r) ? r : (r.results || [])

    if (authStore.isLoggedIn) {
      try {
        const myLikes = await fetchMyLikes('movie')
        if (myLikes.find(item => item.tmdb_id === id)) isLiked.value = true
        
        const myActivity = await fetchMyActivity() 
        const found = myActivity.find(item => item.movie.tmdb_id === id)
        if (found) {
          myReview.value = found
          if (!found.watched) isWished.value = true 
        }
      } catch {}
    }

    try {
      const s = await fetchSimilarMovies(id)
      similarList.value = (s.length > 0) ? s : await fetchFallbackMovies(m.genres[0]?.id, m.id)
    } catch { similarList.value = [] }

  } catch (e) { console.error(e) } 
  finally { loading.value = false }
}

async function fetchFallbackMovies(genreId, currentId) {
  try {
    const res = await fetchMovies({ genre: genreId, page: 1 })
    return (res.results || []).filter(m => m.id !== currentId && m.tmdb_id !== currentId)
  } catch { return [] }
}

// === 이벤트 핸들러 ===
function goPerson(id) {
  router.push({ name: 'person-detail', params: { tmdbId: id } })
}

async function onToggleLike() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    const res = await toggleMovieLike(Number(tmdbId.value))
    isLiked.value = res.liked
    alert(res.liked ? '좋아요 목록에 추가되었습니다!' : '좋아요가 취소되었습니다.')
  } catch { alert('오류가 발생했습니다.') }
}

async function onToggleWish() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    const res = await toggleMovieWish(Number(tmdbId.value))
    isWished.value = res.wished
    if (res.wished) alert('보고싶은 영화에 추가되었습니다.')
    else {
      myReview.value = null
      alert('보고싶은 영화에서 삭제되었습니다.')
    }
    loadAll()
  } catch (err) {
    if (err.response?.data?.detail) alert(err.response.data.detail)
    else alert('오류가 발생했습니다.')
  }
}

// 모달 관련 함수 (Write, List, Detail)
async function openWriteModal() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try { myReview.value = await fetchMyReview(Number(tmdbId.value)) } 
  catch { myReview.value = null }
  showWriteModal.value = true
}

async function handleWriteSubmit(payload) {
  try {
    const body = { content: payload.content, rating: payload.rating, watched: true }
    if (myReview.value?.id) await updateReview(myReview.value.id, body)
    else await createMovieReview(Number(tmdbId.value), body)
    
    showWriteModal.value = false
    await loadAll()
  } catch { alert('저장 실패') }
}

async function handleWriteDelete(reviewId) {
  try {
    await deleteReview(reviewId)
    showWriteModal.value = false
    myReview.value = null
    await loadAll()
  } catch { alert('삭제 실패') }
}

function openListModal() { showListModal.value = true }

function handleSort(sortType) {
  if (sortType === 'likes') reviews.value.sort((a, b) => b.likes_count - a.likes_count)
  else if (sortType === 'latest') reviews.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

async function openDetailModal(review) {
  selectedReview.value = review
  try { reviewComments.value = await fetchReviewComments(review.id) } 
  catch { reviewComments.value = [] }
  showDetailModal.value = true
}

async function handleReviewLike(reviewId) {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    const res = await toggleReviewLike(reviewId)
    if (selectedReview.value?.id === reviewId) {
      selectedReview.value.is_liked = res.liked
      selectedReview.value.likes_count = res.like_count
    }
    const target = reviews.value.find(r => r.id === reviewId)
    if (target) {
      target.is_liked = res.liked
      target.likes_count = res.like_count
    }
  } catch { alert('좋아요 실패') }
}

async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 필요')

  if (content === null) {
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
    return
  }
  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)

    // 🔥 [핵심 추가] 원본 리스트(reviews)에서 해당 리뷰를 찾아 숫자를 직접 올려줍니다.
    const target = reviews.value.find(r => r.id === selectedReview.value.id)
    if (target) {
      target.comments_count = (target.comments_count || 0) + 1
    }

    // 모달창 내부 숫자도 업데이트
    if (selectedReview.value) {
      selectedReview.value.comments_count = (selectedReview.value.comments_count || 0) + 1
    }
  } catch (e) {
    alert('댓글 작성 실패')
  }
}

function handleReplyDelete(commentId) {
  // 1. 모달 내부 리스트에서 제거
  reviewComments.value = reviewComments.value.filter(c => c.id !== commentId)

  // 2. ✅ [수정] 원본 리스트(reviews)에서 해당 리뷰를 찾아 댓글 수 감소
  const target = reviews.value.find(r => r.id === selectedReview.value.id)
  if (target) {
    target.comments_count = Math.max(0, (target.comments_count || 0) - 1)
  }

  // 모달 내부 숫자도 업데이트
  if (selectedReview.value) {
    selectedReview.value.comments_count = Math.max(0, (selectedReview.value.comments_count || 0) - 1)
  }
}

// 초기화 및 와치
onMounted(loadAll)
watch(() => tmdbId.value, loadAll)
</script>

<style scoped>
/* 페이지 레이아웃 및 공통 스타일 */
.page { background-color: #fff; padding-bottom: 100px; min-height: 100vh; }
.loading-screen, .error-screen { padding: 100px; text-align: center; color: #888; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

.body-wrapper { margin-top: 30px; }
.top-section { display: flex; gap: 30px; }
.poster-area { flex-shrink: 0; width: 240px; }
.poster-card { width: 100%; border-radius: 4px; overflow: hidden; border: 1px solid #e3e3e3; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.poster-img { width: 100%; display: block; }
.poster-fallback { height: 350px; background: #eee; display: flex; align-items: center; justify-content: center; color: #aaa; }

.overview { font-size: 15px; line-height: 1.6; color: #4a4a4a; white-space: pre-wrap; margin-top: 20px; }
.section-divider { height: 1px; background: #e3e3e3; margin: 40px 0; }
.sub-title { font-size: 20px; font-weight: 800; color: #000; margin-bottom: 20px; }
.no-data { color: #999; font-size: 14px; padding: 20px 0; }

@media (max-width: 768px) {
  .top-section { flex-direction: column; }
  .poster-area { width: 160px; margin: 0 auto; margin-top: -100px; position: relative; z-index: 10; }
  .poster-card { border: 2px solid white; }
}
</style>