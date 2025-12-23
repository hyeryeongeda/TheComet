<template>
  <form class="form" @submit.prevent="handleSubmit">
    <label class="label">가입 이메일</label>
    <input
      v-model.trim="email"
      class="input"
      type="email"
      autocomplete="email"
      placeholder="user@email.com"
      :disabled="loading"
    />

    <label class="label">생년월일 (선택)</label>
    <input
      v-model="birthDate"
      class="input"
      type="date"
      :disabled="loading"
    />

    <button class="btn" type="submit" :disabled="loading || !email">
      {{ loading ? '처리 중...' : '아이디 안내 메일 받기' }}
    </button>

    <p v-if="success" class="success">{{ success }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { findUsernameApi } from '@/api/comet'

const loading = ref(false)
const error = ref('')
const success = ref('')

const email = ref('')
const birthDate = ref('') // yyyy-mm-dd

async function handleSubmit() {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const payload = { email: email.value }
    if (birthDate.value) payload.birth_date = birthDate.value

    await findUsernameApi(payload)
    success.value = '입력하신 정보와 일치하는 계정이 있으면 이메일로 아이디를 안내했어요.'
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      '요청에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped src="./login.css"></style>
<style scoped>
.success {
  margin: 8px 0 0;
  color: #22c55e;
  font-size: 13px;
  font-weight: 800;
}
</style>
