<template>
  <div class="auth-card">
    <div class="brand">
      <img class="logo" :src="logoSrc" alt="혜성 로고" />
      <h1>혜성</h1>
    </div>

    <LoginForm
      :loading="loading"
      :error="error"
      @submit="$emit('submit', $event)"
    />

    <div class="footer">
      <p>
        아직 계정이 없나요?
        <router-link class="link" to="/signup">회원가입</router-link>
      </p>

      <!-- ✅ 추가: 아이디/비번 찾기 링크 -->
      <p class="helper-links">
        <router-link class="link" to="/find-username">아이디 찾기</router-link>
        <span class="divider">·</span>
        <router-link class="link" to="/reset-password">비밀번호 재설정</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LoginForm from './LoginForm.vue'

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['submit'])

const logoSrc = computed(() => new URL('@/assets/comet_logo.png', import.meta.url).href)
</script>

<style scoped src="./login.css"></style>
