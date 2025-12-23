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
          @toggle-like="handleUnlikePerson"
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
          :key="item.id || item.tmdb_id" 
          :movie="item.movie || item" 
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
// ✅ [수정] 필요한 API 함수들 추가 임포트 (fetchMyLikedPeople, togglePersonLike)
import { fetchMyActivity, fetchMyLikes, fetchMyLikedPeople, togglePersonLike } from '@/api/comet' 

// 컴포넌트 임포트
import SortDropdown from '@/components/ui/SortDropdown.vue'
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' 
import ReviewCard from '@/components/review/ReviewCard.vue'

const route = useRoute()
const type = route.params.type 
const items = ref([])
const loading = ref(false)
const currentSort = ref('latest')

const pageTitle = computed(() => {
  const titles = {
    watched: '봤던 영화',
    wish: '보고싶은 영화',      // 문맥상 '보고싶은 영화'가 맞아서 수정 제안 (원하시는대로 두셔도 됨)
    movie_likes: '좋아요 한 영화', // movie_likes 케이스 추가
    commented: '코멘트 작성한 영화',
    liked_people: '좋아요한 인물',
    liked_reviews: '좋아요한 코멘트'
  }
  return titles[type] || '목록'
})

// ✅ [추가] 인물 좋아요 취소 핸들러
async function handleUnlikePerson(person) {
  // 1. 화면에서 즉시 제거
  items.value = items.value.filter(p => p.tmdb_id !== person.tmdb_id)
  
  // 2. 서버 요청
  try {
    await togglePersonLike(person.tmdb_id)
  } catch (e) {
    console.error('삭제 실패', e)
    alert('오류가 발생했습니다.')
  }
}

async function loadData() {
  loading.value = true
  try {
    // ✅ [수정] 타입별 API 호출 로직 정비
    if (type === 'liked_people') {
      // 인물: 새로 만든 API 사용
      items.value = await fetchMyLikedPeople()
    } 
    else if (type === 'movie_likes') {
      // 영화 좋아요: fetchMyLikes('movie') 사용
      items.value = await fetchMyLikes('movie')
    }
    else if (type === 'liked_reviews') {
      // 리뷰 좋아요
      items.value = await fetchMyActivity({ status: 'liked', sort: currentSort.value })
    } 
    else {
      // 나머지 (commented, wish 등)
      items.value = await fetchMyActivity({ status: type, sort: currentSort.value })
    }
  } catch (e) {
    console.error("데이터 로딩 실패:", e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 20px 14px 60px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 2px solid #eee; }
.title { font-size: 22px; font-weight: 900; margin: 0; }
.loading, .empty { padding: 40px; text-align: center; color: #888; }

.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

@media (min-width: 600px) { .grid-container { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 900px) { .grid-container { grid-template-columns: repeat(5, 1fr); } }
</style>