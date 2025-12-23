<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-window">
      <div class="header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="user-list">
        <div v-if="users.length === 0" class="empty">목록이 비어있습니다.</div>
        
        <div v-for="user in users" :key="user.id" class="user-item">
          <div class="user-info" @click="goProfile(user.username)">
            <img v-if="user.profile_image" :src="fullUrl(user.profile_image)" class="avatar" />
            <div v-else class="avatar-fallback">👤</div>
            <span class="username">{{ user.username }}</span>
          </div>
          
          </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: String,
  users: Array
})
const emit = defineEmits(['close'])
const router = useRouter()

function fullUrl(path) {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://127.0.0.1:8000${path}`
}

function goProfile(username) {
  emit('close') // 이동 전 모달 닫기
  router.push(`/user/${username}`)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.modal-window {
  background: white; width: 400px; height: 500px; border-radius: 12px;
  display: flex; flex-direction: column; overflow: hidden;
}
.header {
  padding: 15px 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.header h3 { margin: 0; font-size: 18px; font-weight: 800; }
.close-btn { border: none; background: none; font-size: 20px; cursor: pointer; }

.user-list { flex: 1; overflow-y: auto; padding: 10px; }
.empty { text-align: center; color: #999; margin-top: 50px; }

.user-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px; border-radius: 8px; transition: background 0.2s;
}
.user-item:hover { background: #f9f9f9; }

.user-info { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 1px solid #eee; }
.avatar-fallback { 
  width: 40px; height: 40px; border-radius: 50%; background: #eee; 
  display: flex; align-items: center; justify-content: center; font-size: 20px; 
}
.username { font-weight: 700; font-size: 15px; }
</style>