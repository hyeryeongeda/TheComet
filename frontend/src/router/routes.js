// frontend/src/router/routes.js

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/movies', name: 'movies', component: () => import('@/views/MoviesView.vue') },
  {
    path: '/movies/:tmdbId',
    name: 'movie-detail',
    component: () => import('@/views/MovieDetailView.vue'),
    props: true,
  },

  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/signup', name: 'signup', component: () => import('@/views/SignupView.vue') },

  {
    path: '/taste',
    name: 'taste',
    component: () => import('@/views/TasteView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recommend',
    name: 'recommend',
    component: () => import('@/views/RecommendView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/search', name: 'search', component: () => import('@/views/SearchView.vue') },

  // ✅ 마이페이지는 /mypage로 통일
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true },
  },

  // ✅ 기존 /me 호환
  { path: '/me', redirect: { name: 'mypage' } },

  {
    path: '/users/:username',
    name: 'user-profile',
    component: () => import('@/views/UserProfileView.vue'),
    props: true,
  },

  { path: '/:pathMatch(.*)*', name: 'notfound', component: () => import('@/views/NotFoundView.vue') },
  { path: '/people/:tmdbId', name: 'person-detail', component: () => import('@/views/PersonDetailView.vue'), props: true },


  // 기존 routes 배열 안에 추가 [마이페이지]
  { 
    path: '/mypage/list/:type', 
    name: 'mypage-grid', 
    component: () => import('@/views/MyPageGridView.vue'),
    props: true,
    meta: { requiresAuth: true }
  },





]

export default routes
