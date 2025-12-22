<template>
  <div class="page">
    <header class="header">
      <h2 class="title">{{ pageTitle }}</h2>
      <SortDropdown 
        v-if="type !== 'liked_people'"
        v-model="currentSort" 
        @update:modelValue="loadData" 
      />
    </header>

    <div v-if="loading" class="loading">로딩중...</div>
    
    <div v-else-if="items.length > 0" class="grid-container">
      
      <template v-if="type === 'liked_people'">
        <PersonCard 
          v-for="item in items" 
          :key="item.tmdb_id" 
          :person="item" 
        />
      </template>

      <template v-else-if="type === 'liked_reviews'">
        <ReviewCard 
          v-for="item in items" 
          :key="item.id" 
          :review="item" 
        />
      </template>

      <template v-else>
        <MovieCard 
          v-for="item in items" 
          :key="item.id" 
          :movie="item.movie" 
          class="card-item"
        />
      </template>

    </div>

    <div v-else class="empty">
      보관된 데이터가 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
// fetchMyLikes 추가됨
import { fetchMyActivity, fetchMyLikes } from '@/api/comet' 

// 컴포넌트 임포트
import SortDropdown from '@/components/ui/SortDropdown.vue'
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' // 추가
import ReviewCard from '@/components/review/ReviewCard.vue' // 추가

const route = useRoute()
const type = route.params.type 
// type 종류: 'watched', 'wish', 'commented', 'liked_people', 'liked_reviews'

const items = ref([])
const loading = ref(false)
const currentSort = ref('latest')

// 페이지 제목 결정
const pageTitle = computed(() => {
  if (type === 'watched') return '봤던 영화'
  if (type === 'wish') return '보고싶은 영화'
  if (type === 'commented') return '코멘트 작성한 영화'
  if (type === 'liked_people') return '좋아요한 인물'
  if (type === 'liked_reviews') return '좋아요한 코멘트'
  return '목록'
})

async function loadData() {
  loading.value = true
  items.value = [] // 초기화

  try {
    if (type === 'liked_people') {
      // 1. 인물 좋아요 목록 (정렬 없음)
      const res = await fetchMyLikes('person')
      items.value = res
    } else if (type === 'liked_reviews') {
      // 2. 리뷰 좋아요 목록 (정렬 가능 - 백엔드 지원 시)
      const res = await fetchMyActivity({ status: 'liked', sort: currentSort.value })
      items.value = res
    } else {
      // 3. 기존 영화 목록 (watched, wish, commented)
      const res = await fetchMyActivity({ status: type, sort: currentSort.value })
      items.value = res 
    }
  } catch (e) {
    console.error("데이터 로딩 실패:", e)
  } finally {
    loading.value = false
  }
}

// 라우터 파라미터가 바뀌어도 컴포넌트가 재활용될 수 있으므로 watch 추가 (선택사항이나 안전함)
watch(() => route.params.type, () => {
  // 페이지 이동 시 데이터 새로고침 필요하면 여기서 처리 (현재 구조에선 onMounted로 충분할 수 있음)
})

onMounted(loadData)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 20px 14px 60px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 2px solid var(--text); }
.title { font-size: 22px; font-weight: 900; margin: 0; color: var(--text); }
.loading, .empty { padding: 40px; text-align: center; color: var(--muted); }

/* 반응형 그리드 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 모바일: 2열 */
  gap: 14px;
}

/* ReviewCard는 가로로 좀 더 길어야 예쁠 수 있지만, 일단 그리드에 맞춤 */
@media (min-width: 500px) { .grid-container { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 768px) { .grid-container { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1024px) { .grid-container { grid-template-columns: repeat(5, 1fr); } }
</style>