<template>
  <div class="page">
    <section class="hero">
      <h1 class="hero-title">지금 뭐 볼까?</h1>
      <p class="hero-sub">인기 / 최신 / 극찬작을 한 번에 둘러보자.</p>
    </section>

    <hr class="divider" />

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">지금 뜨는 인기 영화</h2>
        <button class="more" @click="goMovies('popular')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="인기 영화" :movies="popular" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최신 개봉 작품</h2>
        <button class="more" @click="goMovies('latest')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="최신 개봉작" :movies="nowPlaying" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">평론가가 극찬한 영화</h2>
        <button class="more" @click="goMovies('rating')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="평론가 극찬작" :movies="topRated" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최근 코멘트</h2>
        <button class="more" @click="go('/mypage')">더보기</button>
      </div>
      <p v-if="reviewsLoading" class="muted">불러오는 중...</p>
      
      <div class="review-slider-wrapper">
        <button class="nav-btn left" @click="scrollPrev">‹</button>

        <div class="review-scroll-container" ref="scrollContainer">
          <ReviewCard
            v-for="r in recentReviews"
            :key="r.id"
            :review="r"
            class="slider-item"
            @click="openReviewModal(r)"
          />
        </div>

        <button class="nav-btn right" @click="scrollNext">›</button>
      </div>
    </section>

    <ReviewDetailModal
      v-if="showDetailModal && selectedReview"
      :review="selectedReview"
      :replies="reviewComments"
      :movie="selectedReview.movie" 
      @close="closeDetailModal"
      @submit-reply="handleReplySubmit"
      @toggle-like="handleReviewLike"
      @delete-reply="handleReplyDelete"
      @delete-review="handleReviewDeleteLocal"
      @update-review="handleReviewUpdateLocal"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  fetchHomeSections, 
  fetchRecentReviews, 
  fetchReviewComments, 
  createReviewComment, 
  toggleReviewLike 
} from '@/api/comet.js'

import MovieRow from '@/components/movie/MovieRow.vue'
import ReviewCard from '@/components/review/ReviewCard.vue'
import ReviewDetailModal from '@/components/review/ReviewDetailModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])
const reviewsLoading = ref(false)
const recentReviews = ref([])

// 모달 상태
const showDetailModal = ref(false)
const selectedReview = ref(null)
const reviewComments = ref([])

async function loadHome() {
  loading.value = true
  try {
    const data = await fetchHomeSections(1)
    popular.value = data?.popular ?? []
    nowPlaying.value = data?.now_playing ?? []
    topRated.value = data?.top_rated ?? []
  } finally {
    loading.value = false
  }
}

async function loadRecentReviews() {
  reviewsLoading.value = true
  try {
    const data = await fetchRecentReviews(12)
    recentReviews.value = Array.isArray(data) ? data : (data?.results || [])
  } finally {
    reviewsLoading.value = false
  }
}

// [모달 열기]
async function openReviewModal(review) {
  selectedReview.value = review
  try {
    const res = await fetchReviewComments(review.id)
    reviewComments.value = res || []
  } catch (e) {
    reviewComments.value = []
  }
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedReview.value = null
}

// 🔥 [삭제 반영] 리스트에서 리뷰 삭제 (새로고침 없이 반영)
function handleReviewDeleteLocal(reviewId) {
  recentReviews.value = recentReviews.value.filter(r => r.id !== reviewId)
  closeDetailModal()
}

// 🔥 [수정 반영] 리스트에 수정 내용 덮어쓰기 (새로고침 없이 반영)
function handleReviewUpdateLocal(updatedReview) {
  // 리스트에서 찾아서 업데이트
  const idx = recentReviews.value.findIndex(r => r.id === updatedReview.id)
  if (idx !== -1) {
    recentReviews.value[idx] = { ...recentReviews.value[idx], ...updatedReview }
  }
  
  // 모달에 떠있는 데이터도 업데이트 (이게 없으면 모달 닫기 전까지 옛날 내용 보임)
  if (selectedReview.value && selectedReview.value.id === updatedReview.id) {
    selectedReview.value = { ...selectedReview.value, ...updatedReview }
  }
}
const scrollContainer = ref(null)

// 왼쪽으로 이동
const scrollPrev = () => {
  if (scrollContainer.value) {
    // 현재 컨테이너 너비만큼 왼쪽으로 부드럽게 이동
    scrollContainer.value.scrollBy({
      left: -scrollContainer.value.clientWidth,
      behavior: 'smooth'
    })
  }
}

// 오른쪽으로 이동
const scrollNext = () => {
  if (scrollContainer.value) {
    // 현재 컨테이너 너비만큼 오른쪽으로 부드럽게 이동
    scrollContainer.value.scrollBy({
      left: scrollContainer.value.clientWidth,
      behavior: 'smooth'
    })
  }
}
// [댓글 작성]
async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
  } catch (e) {
    alert('댓글 작성 실패')
  }
}

// [댓글 삭제]
function handleReplyDelete(commentId) {
  reviewComments.value = reviewComments.value.filter(c => c.id !== commentId)
}

// [좋아요 토글]
async function handleReviewLike(reviewId) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    const res = await toggleReviewLike(reviewId)
    if (selectedReview.value) {
      selectedReview.value.is_liked = res.liked
      selectedReview.value.likes_count = res.like_count
    }
    const target = recentReviews.value.find(r => r.id === reviewId)
    if (target) {
      target.is_liked = res.liked
      target.likes_count = res.like_count
    }
  } catch (e) {
    alert('오류 발생')
  }
}

function goDetail(movie) {
  const tmdbId = movie?.tmdb_id ?? movie?.id
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}

function goMovies(sort) {
  router.push({ path: '/movies', query: { sort } })
}

function go(path) {
  router.push(path)
}

onMounted(() => {
  loadHome()
  loadRecentReviews()
})
</script>

<style scoped>
/* 1. 기본 레이아웃 및 텍스트 (테마 대응) */
.page { 
  max-width: 1100px; 
  margin: 0 auto; 
  padding: 20px 14px 60px; 
  color: var(--text); /* #111 -> 테마 적용 */
}

.hero { padding: 26px 0 18px; }
.hero-title { 
  margin: 0; 
  font-size: 44px; 
  font-weight: 900; 
  letter-spacing: -0.02em; 
  color: var(--text); 
}
.hero-sub { 
  margin: 10px 0 0; 
  color: var(--muted); /* #666 -> 테마 적용 */
  font-weight: 700; 
}

.divider { 
  border: none; 
  border-top: 1px solid var(--border); /* #eee -> 테마 적용 */
  margin: 18px 0 22px; 
}

.sec { margin-top: 18px; }
.sec-head { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  gap: 10px; 
  margin-bottom: 10px; 
}
.sec-title { 
  margin: 0; 
  font-size: 18px; 
  font-weight: 900; 
  color: var(--text);
}

.more { 
  border: none; 
  background: transparent; 
  cursor: pointer; 
  color: var(--muted); 
  font-weight: 900; 
}
.more:hover { 
  text-decoration: underline; 
  color: var(--primary); 
}

.muted { color: var(--muted); margin: 10px 0 0; }

/* 2. 슬라이더 래퍼 */
.review-slider-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

/* 3. 리뷰 그리드 컨테이너 (핵심: 3열 2행 설정) */
.review-scroll-container {
  display: grid;
  /* ✅ 2줄(행)로 고정 */
  grid-template-rows: repeat(2, 1fr); 
  /* ✅ 아이템을 위->아래로 먼저 채우고 가로(열)로 확장 */
  grid-auto-flow: column; 
  /* ✅ 한 화면에 3개씩 노출 (간격 16px을 고려한 계산값) */
  grid-auto-columns: calc(33.333% - 10.7px); 
  
  gap: 16px; 
  overflow-x: auto; 
  scroll-behavior: smooth; 
  scroll-snap-type: x mandatory; 
  padding: 10px 0;
  
  /* 스크롤바 숨기기 */
  scrollbar-width: none; /* 파이어폭스 */
  -ms-overflow-style: none; /* IE */
}

/* 크롬, 사파리 스크롤바 숨기기 */
.review-scroll-container::-webkit-scrollbar {
  display: none;
}

.slider-item {
  width: 100%;
  scroll-snap-align: start; /* 넘길 때 시작점에 딱 붙음 */
}

/* 4. 네비게이션 버튼 스타일 */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--card); /* 테마 배경색 */
  border: 1px solid var(--border);
  color: var(--text);
  box-shadow: var(--shadow);
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  transform: translateY(-50%) scale(1.1); /* 살짝 커지는 효과 */
}

/* 버튼 위치 조정 */
.nav-btn.left { left: -22px; }
.nav-btn.right { right: -22px; }

.chevron {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
}

/* 5. 반응형 대응 (화면 크기에 따라 열 개수 조절) */
@media (max-width: 768px) {
  .review-scroll-container {
    /* 태블릿: 2열 2행으로 변경 */
    grid-auto-columns: calc(50% - 8px); 
  }
}

@media (max-width: 480px) {
  .review-scroll-container {
    /* 모바일: 1줄로 변경하고 85% 너비로 다음 카드 살짝 보이게 */
    grid-template-rows: repeat(1, 1fr); 
    grid-auto-columns: 85%;
    padding: 0 10px;
  }
}
</style>