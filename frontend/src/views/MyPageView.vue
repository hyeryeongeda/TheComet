<template>
  <div class="page">
    
    <section class="profile-card">
      <div class="avatar-area">
        <div class="avatar">
           <img v-if="user?.profile_image" :src="user.profile_image" alt="profile" />
           <div v-else class="fallback">👤</div>
        </div>
        <div class="names">
          <h1 class="username">{{ user?.username || '사용자' }}</h1>
          <button class="btn-edit" @click="openEdit = true">프로필 수정</button>
        </div>
      </div>
      <div class="stats">
        <div class="stat-item"><span>팔로잉</span> <b>{{ user?.following_count || 0 }}</b></div>
        <div class="stat-item"><span>팔로워</span> <b>{{ user?.followers_count || 0 }}</b></div>
      </div>
    </section>

    <div class="tabs">
      <button :class="['tab', { active: tab === 'vault' }]" @click="tab = 'vault'">보관함</button>
      <button :class="['tab', { active: tab === 'likes' }]" @click="tab = 'likes'">좋아요</button>
    </div>

    <div v-if="tab === 'vault'" class="content">
      
      <section class="row-section">
        <div class="head">
          <h3>코멘트 영화 (작성한)</h3>
          <router-link :to="{ name: 'mypage-grid', params: { type: 'commented' }}" class="more">더보기 ></router-link>
        </div>
        <div class="row-list">
          <MovieCard v-for="item in commentedList.slice(0, 5)" :key="item.id" :movie="item.movie" />
          <div v-if="commentedList.length === 0" class="empty-msg">작성한 코멘트가 없습니다.</div>
        </div>
      </section>

      <section class="row-section">
        <div class="head">
          <h3>보고싶은 영화</h3>
          <router-link :to="{ name: 'mypage-grid', params: { type: 'wish' }}" class="more">더보기 ></router-link>
        </div>
        <div class="row-list">
          <MovieCard v-for="item in wishList.slice(0, 5)" :key="item.id" :movie="item.movie" />
          <div v-if="wishList.length === 0" class="empty-msg">보고싶은 영화가 없습니다.</div>
        </div>
      </section>

      <section class="row-section">
        <div class="head">
          <h3>봤던 영화</h3>
          <router-link :to="{ name: 'mypage-grid', params: { type: 'watched' }}" class="more">더보기 ></router-link>
        </div>
        <div class="row-list">
          <MovieCard v-for="item in watchedList.slice(0, 5)" :key="item.id" :movie="item.movie" />
          <div v-if="watchedList.length === 0" class="empty-msg">봤던 영화가 없습니다.</div>
        </div>
      </section>
    </div>

    <div v-else class="content">
      
      <section class="row-section">
        <div class="head">
          <h3>인물 (자신이 좋아요를 누른)</h3>
          <router-link :to="{ name: 'mypage-grid', params: { type: 'liked_people' }}" class="more">더보기 ></router-link>
        </div>
        <div class="row-list">
          <PersonCard v-for="p in likedPeople.slice(0, 5)" :key="p.tmdb_id" :person="p" />
          <div v-if="likedPeople.length === 0" class="empty-msg">좋아요한 인물이 없습니다.</div>
        </div>
      </section>

      <section class="row-section">
        <div class="head">
          <h3>장르 (자신이 좋아요를 누른)</h3>
        </div>
        <div class="genre-list">
          <div v-for="g in likedGenres" :key="g.tmdb_id" class="genre-pill">
            {{ g.name }}
          </div>
          <div v-if="likedGenres.length === 0" class="empty-msg">좋아요한 장르가 없습니다.</div>
        </div>
      </section>

      <section class="row-section">
        <div class="head">
          <h3>코멘트 (자신이 좋아요를 누른)</h3>
          <router-link :to="{ name: 'mypage-grid', params: { type: 'liked_reviews' }}" class="more">더보기 ></router-link>
        </div>
        <div class="row-list">
          <ReviewCard v-for="r in likedReviews.slice(0, 5)" :key="r.id" :review="r" />
          <div v-if="likedReviews.length === 0" class="empty-msg">좋아요한 코멘트가 없습니다.</div>
        </div>
      </section>
    </div>

    <ProfileEditModal 
      v-if="openEdit" 
      :user="user" 
      @close="openEdit = false"
      @saved="onProfileSaved" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchMyActivity, fetchMyLikes } from '@/api/comet' 

// 컴포넌트들
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' 
import ReviewCard from '@/components/review/ReviewCard.vue'
import ProfileEditModal from '@/components/user/ProfileEditModal.vue' 

const auth = useAuthStore()
const user = ref(auth.user)
const tab = ref('vault')
const openEdit = ref(false)

const commentedList = ref([])
const wishList = ref([])
const watchedList = ref([])
const likedPeople = ref([])
const likedGenres = ref([])
const likedReviews = ref([])

// 프로필 수정 후 화면 갱신 함수 (추가됨)
function onProfileSaved(updatedUser) {
  // 로컬 상태 업데이트 (화면 즉시 반영)
  user.value = { ...user.value, ...updatedUser }
  // Pinia 스토어 상태도 업데이트 (다른 페이지 이동 시 유지)
  auth.user = user.value
}

onMounted(async () => {
  try {
    const [
      commented, 
      wish, 
      watched,
      people,
      genres,
      reviews
    ] = await Promise.all([
      fetchMyActivity({ status: 'commented', sort: 'latest' }),
      fetchMyActivity({ status: 'wish', sort: 'latest' }),
      fetchMyActivity({ status: 'watched', sort: 'latest' }),
      fetchMyLikes('person'),
      fetchMyLikes('genre'),
      fetchMyActivity({ status: 'liked', sort: 'latest' })
    ])
    
    commentedList.value = commented
    wishList.value = wish
    watchedList.value = watched
    likedPeople.value = people
    likedGenres.value = genres
    likedReviews.value = reviews

  } catch (error) {
    console.error("데이터를 가져오는 중 오류 발생:", error)
  }
})
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 30px 14px; }

/* 프로필 영역 */
.profile-card { text-align: center; margin-bottom: 30px; }
.avatar-area { margin-bottom: 20px; }
.avatar { width: 100px; height: 100px; background: #eee; border-radius: 50%; margin: 0 auto 10px; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border); }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.fallback { font-size: 40px; }
.names { margin-top: 10px; }
.username { font-size: 24px; font-weight: 900; margin-bottom: 10px; color: var(--text); }
.btn-edit { padding: 6px 12px; border: 1px solid var(--border); background: var(--card); border-radius: 4px; cursor: pointer; font-size: 13px; color: var(--text); }
.stats { display: flex; justify-content: center; gap: 20px; color: var(--muted); font-size: 14px; }
.stats b { color: var(--text); font-weight: 900; margin-left: 4px; }

/* 탭 메뉴 */
.tabs { display: flex; border-bottom: 2px solid var(--border); margin-bottom: 30px; }
.tab { flex: 1; padding: 14px; font-size: 16px; font-weight: 700; background: none; border: none; cursor: pointer; color: var(--muted); }
.tab.active { color: var(--text); border-bottom: 2px solid var(--text); margin-bottom: -2px; }

/* 섹션 공통 */
.row-section { margin-bottom: 40px; }
.head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 14px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
.head h3 { font-size: 20px; font-weight: 800; margin: 0; color: var(--text); }
.more { font-size: 13px; color: var(--muted); text-decoration: none; }
.more:hover { color: var(--text); }

/* 가로 스크롤 리스트 */
.row-list { display: flex; gap: 14px; overflow-x: auto; padding-bottom: 10px; scroll-behavior: smooth; }
.row-list::-webkit-scrollbar { height: 6px; }
.row-list::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }

/* 데이터 없을 때 메시지 */
.empty-msg { width: 100%; padding: 20px 0; color: var(--muted); font-size: 14px; }

/* 장르 태그 스타일 */
.genre-list { display: flex; flex-wrap: wrap; gap: 10px; }
.genre-pill { 
  padding: 8px 16px; 
  border-radius: 99px; 
  background: var(--input-bg); 
  border: 1px solid var(--border); 
  color: var(--text);
  font-weight: 700; 
  font-size: 14px;
}
</style>