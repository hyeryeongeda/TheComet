<template>
  <BaseModal :open="true" title="프로필 수정" @close="emit('close')">
    <div class="form">
      <div class="image-edit">
        <div class="avatar-preview">
          <img 
            :src="avatarSrc" 
            alt="Profile" 
            @error="(e) => (e.target.src = '/default-avatar.png')" 
          />
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          hidden
          @change="onFileChange"
        />
        <button type="button" class="btn-sub" @click="openFilePicker">사진 변경</button>
      </div>

      <label class="label">아이디</label>
      <input class="input readonly" :value="user?.username" readonly />

      <label class="label">이름</label>
      <input class="input" v-model="form.name" placeholder="이름을 입력하세요" />

      <hr class="divider" />
      <h4 class="sub-title">비밀번호 변경</h4>

      <label class="label">현재 비밀번호</label>
      <input
        class="input"
        v-model="form.old_password"
        type="password"
        placeholder="기존 비밀번호"
        autocomplete="current-password"
      />

      <label class="label">새 비밀번호</label>
      <input
        class="input"
        v-model="form.new_password"
        type="password"
        placeholder="새 비밀번호 (선택)"
        autocomplete="new-password"
      />

      <div class="modal-actions">
        <button type="button" class="btn ghost" @click="emit('close')">취소</button>
        <button type="button" class="btn" @click="handleSave" :disabled="loading">
          {{ loading ? '저장 중...' : '저장하기' }}
        </button>
      </div>

      <p v-if="error" class="err-msg">{{ error }}</p>

      <hr class="divider" />
      <div class="danger-zone">
        <h4 class="danger-title">계정 관리</h4>
        <p class="danger-desc">
          회원탈퇴 시 계정이 비활성화되며 다시 로그인할 수 없습니다.
        </p>

        <button type="button" class="btn-danger" @click="toggleWithdraw">
          {{ showWithdraw ? '탈퇴 취소' : '회원탈퇴' }}
        </button>

        <div v-if="showWithdraw" class="withdraw-box">
          <label class="label">비밀번호 확인</label>
          <input
            class="input"
            v-model="withdraw.password"
            type="password"
            placeholder="현재 비밀번호 입력"
          />

          <label class="check">
            <input type="checkbox" v-model="withdraw.agree" />
            <span>안내사항을 확인했으며, 탈퇴에 동의합니다.</span>
          </label>

          <div class="withdraw-actions">
            <button
              type="button"
              class="btn-danger solid"
              @click="handleWithdraw"
              :disabled="withdraw.loading || !withdraw.agree"
            >
              {{ withdraw.loading ? '처리 중...' : '탈퇴 확정' }}
            </button>
          </div>
          <p v-if="withdraw.error" class="err-msg">{{ withdraw.error }}</p>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseModal from '@/components/ui/BaseModal.vue'
import { updateMyProfile, withdrawAccount } from '@/api/comet'

const props = defineProps({
  user: Object,
})
const emit = defineEmits(['close', 'saved'])

const router = useRouter()
const authStore = useAuthStore()

// --- 상태 관리 ---
const loading = ref(false)
const error = ref('')
const previewUrl = ref(null)
const selectedFile = ref(null)
const fileInput = ref(null)

const form = reactive({
  name: props.user?.name || '',
  old_password: '',
  new_password: '',
})

const showWithdraw = ref(false)
const withdraw = reactive({
  password: '',
  agree: false,
  loading: false,
  error: '',
})

// --- 이미지 경로 처리 (핵심 수정) ---
const avatarSrc = computed(() => {
  // 1. 사용자가 새로 선택한 미리보기 파일이 있다면 최우선
  if (previewUrl.value) return previewUrl.value

  // 2. 서버에서 넘어온 프로필 이미지가 있다면
  if (props.user?.profile_image) {
    const path = props.user.profile_image
    // 이미 전체 주소(http...)라면 그대로 반환, 아니라면 백엔드 주소 결합
    return path.startsWith('http') ? path : `http://localhost:8000${path}`
  }

  // 3. 둘 다 없으면 기본 이미지
  return '/default-avatar.png'
})

// --- 파일 관련 로직 ---
function openFilePicker() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return

  // 기존 미리보기 URL 메모리 해제 (성능 최적화)
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)

  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

// 컴포넌트가 사라질 때 가비지 컬렉션
onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

// --- API 연동 로직 ---
async function handleSave() {
  if (loading.value) return
  loading.value = true
  error.value = ''

  try {
    const fd = new FormData()
    fd.append('name', form.name)
    if (selectedFile.value) fd.append('profile_image', selectedFile.value)
    
    // 비밀번호 필드 처리
    if (form.old_password && form.new_password) {
      fd.append('old_password', form.old_password)
      fd.append('new_password', form.new_password)
    }

    const updatedUser = await updateMyProfile(fd)
    emit('saved', updatedUser)
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || '수정에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// --- 회원 탈퇴 로직 ---
function toggleWithdraw() {
  showWithdraw.value = !showWithdraw.value
}

async function handleWithdraw() {
  if (!withdraw.agree || withdraw.loading) return
  withdraw.loading = true
  withdraw.error = ''

  try {
    await withdrawAccount(withdraw.password)
    await authStore.logout() // store에 정의된 로그아웃 호출
    emit('close')
    router.push('/')
  } catch (err) {
    withdraw.error = err.response?.data?.detail || '탈퇴 실패: 비밀번호를 확인하세요.'
  } finally {
    withdraw.loading = false
  }
}
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
}

.image-edit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.avatar-preview {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--border);
  background: var(--bg);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-sub {
  font-size: 12px;
  padding: 4px 8px;
  cursor: pointer;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text);
  transition: background 0.2s;
}

.btn-sub:hover {
  background: var(--primary-weak);
}

.label {
  font-size: 13px;
  font-weight: 800;
  color: var(--muted);
  margin-top: 5px;
}

.input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
  outline: none;
  transition: border-color 0.2s;
}

.input:focus {
  border-color: var(--primary);
}

.input.readonly {
  background: var(--primary-weak);
  color: var(--muted);
  border-color: var(--border);
  opacity: 0.7;
  outline: none;
}

.divider {
  margin: 15px 0;
  border: 0;
  border-top: 1px solid var(--border);
}

.sub-title {
  font-size: 14px;
  font-weight: 900;
  margin-bottom: 5px;
  color: var(--text);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  border: 1px solid var(--primary);
  transition: all 0.2s;
}

.btn.ghost {
  background: var(--card);
  color: var(--text);
  border-color: var(--border);
}

.btn.ghost:hover {
  background: var(--bg);
}

.btn:not(.ghost) {
  background: var(--primary);
  color: #ffffff;
}

.btn:not(.ghost):hover {
  filter: brightness(1.1);
  box-shadow: var(--shadow);
}

.err-msg {
  color: #ff4d4f;
  font-size: 12px;
  text-align: center;
  margin-top: 10px;
  font-weight: 700;
}

/* -----------------------------
  Danger zone
----------------------------- */
.danger-zone {
  margin-top: 10px;
  padding: 12px;
  border: 1px solid rgba(255, 77, 79, 0.35);
  border-radius: 12px;
  background: rgba(255, 77, 79, 0.06);
}

.danger-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 900;
  color: #ff4d4f;
}

.danger-desc {
  margin: 0 0 10px;
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
  line-height: 1.4;
}

.btn-danger {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #ff4d4f;
  background: transparent;
  color: #ff4d4f;
  font-weight: 900;
  cursor: pointer;
  transition: filter 0.2s, opacity 0.2s;
}

.btn-danger:hover {
  filter: brightness(1.05);
}

.btn-danger.solid {
  background: #ff4d4f;
  color: #fff;
}

.withdraw-box {
  margin-top: 12px;
  display: grid;
  gap: 10px;
}

.check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text);
}

.withdraw-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
