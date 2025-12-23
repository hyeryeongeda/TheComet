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

    <button class="btn" type="submit" :disabled="loading || !email">
      {{ loading ? '전송 중...' : '재설정 링크 받기' }}
    </button>

    <p v-if="success" class="success">{{ success }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { passwordResetRequestApi } from '@/api/comet'

const loading = ref(false)
const error = ref('')
const success = ref('')

const email = ref('')

async function handleSubmit() {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await passwordResetRequestApi({ email: email.value })
    success.value = '해당 이메일의 계정이 존재하면 재설정 링크를 전송했어요. 메일함을 확인해 주세요.'
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
