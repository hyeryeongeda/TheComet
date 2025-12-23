<template>
  <form class="form" @submit.prevent="handleSubmit">
    <label class="label">새 비밀번호</label>
    <input
      v-model="pw1"
      class="input"
      type="password"
      autocomplete="new-password"
      placeholder="8자 이상"
      :disabled="loading"
    />

    <label class="label">새 비밀번호 확인</label>
    <input
      v-model="pw2"
      class="input"
      type="password"
      autocomplete="new-password"
      placeholder="한 번 더 입력"
      :disabled="loading"
    />

    <button class="btn" type="submit" :disabled="loading || !pw1 || !pw2">
      {{ loading ? '변경 중...' : '비밀번호 변경하기' }}
    </button>

    <p v-if="success" class="success">{{ success }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { passwordResetConfirmApi } from '@/api/comet'

const props = defineProps({
  uid: { type: String, required: true },
  token: { type: String, required: true },
})

const emit = defineEmits(['done'])

const loading = ref(false)
const error = ref('')
const success = ref('')

const pw1 = ref('')
const pw2 = ref('')

async function handleSubmit() {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await passwordResetConfirmApi({
      uid: props.uid,
      token: props.token,
      new_password: pw1.value,
      new_password2: pw2.value,
    })
    success.value = '비밀번호가 변경되었습니다. 잠시 후 로그인 화면으로 이동합니다.'
    emit('done')
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      '변경에 실패했습니다.'
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
