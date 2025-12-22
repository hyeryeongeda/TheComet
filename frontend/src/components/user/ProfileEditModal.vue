<template>
  <Teleport to="body">
    <div class="backdrop" @click.self="$emit('close')">
      <div class="modal-card">
        <h3 class="title">프로필 수정</h3>

        <div class="body">
          <div class="upload-area">
            <div class="preview-box" @click="triggerFileSelect">
              <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="preview" />
              <div v-else class="upload-placeholder">
                <span class="plus">+</span>
                <span class="text">Upload</span>
              </div>
            </div>
            <input 
              ref="fileInput" 
              type="file" 
              accept="image/*" 
              class="hidden-input"
              @change="onFileChange"
            />
            <p class="guide-text">
              이미지를 변경하려면 위 영역을 클릭하세요.
            </p>
          </div>

          <div class="input-group">
            
            <div class="input-area">
              <label class="label">닉네임 (아이디)</label>
              <input 
                v-model="form.username" 
                type="text" 
                class="input" 
                placeholder="새로운 닉네임"
              />
            </div>

            <div class="input-area">
              <label class="label">이름</label>
              <input 
                v-model="form.name" 
                type="text" 
                class="input" 
                placeholder="이름"
                maxlength="20"
              />
              <div class="counter">{{ form.name.length }}/20</div>
            </div>

          </div>
        </div>

        <button class="btn-confirm" @click="save" :disabled="loading">
          {{ loading ? '저장 중...' : '확인' }}
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { updateMyProfile } from '@/api/comet'

const props = defineProps({
  user: { type: Object, required: true }
})
const emit = defineEmits(['close', 'saved'])

const fileInput = ref(null)
const loading = ref(false)
const previewUrl = ref('')
const selectedFile = ref(null) // 실제 업로드할 파일 객체

const form = reactive({
  username: '', 
  name: ''
})

onMounted(() => {
  // 기존 정보 채우기
  form.username = props.user.username || ''
  form.name = props.user.name || ''
  // 백엔드에서 이미지 URL이 오면 전체 경로가 아닐 수 있으므로 처리 필요할 수 있음
  // 보통 http://... 로 오면 그대로 씀
  previewUrl.value = props.user.profile_image || ''
})

function triggerFileSelect() {
  fileInput.value.click()
}

function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    // 화면 표시용 (미리보기)
    previewUrl.value = URL.createObjectURL(file)
  }
}

async function save() {
  loading.value = true
  try {
    // [중요] 파일을 전송하려면 FormData 객체를 사용해야 합니다.
    const formData = new FormData()
    
    // 1. 텍스트 데이터 추가
    formData.append('name', form.name)
    formData.append('username', form.username)

    // 2. 파일 데이터 추가 (파일을 선택했을 때만)
    if (selectedFile.value) {
      // 'profile_image'는 백엔드 모델의 필드명과 일치해야 합니다.
      formData.append('profile_image', selectedFile.value)
    }

    // 3. API 호출 (FormData를 보내면 axios가 자동으로 multipart/form-data 처리)
    const updatedUser = await updateMyProfile(formData)
    
    // 4. 성공 시 부모 컴포넌트에 알림
    emit('saved', updatedUser) // 백엔드가 반환한 최신 유저 정보 사용
    emit('close')
    alert('프로필이 수정되었습니다!')
    
  } catch (e) {
    console.error(e)
    const errorMsg = e.response?.data?.username?.[0] || e.response?.data?.detail || e.message
    alert('프로필 수정 실패: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999;
}
.modal-card {
  width: 320px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.title { margin: 0 0 20px; font-size: 18px; font-weight: 800; color: #111; }

.upload-area {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; margin-bottom: 20px;
}
.preview-box {
  width: 80px; height: 80px;
  border: 1px dashed #ccc; border-radius: 8px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; position: relative;
}
.preview-box:hover { background: #f9f9f9; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.upload-placeholder { color: #999; display: flex; flex-direction: column; align-items: center; }
.plus { font-size: 20px; line-height: 1; }
.text { font-size: 10px; margin-top: 2px; }
.hidden-input { display: none; }
.guide-text {
  font-size: 12px; color: #ff4d4f; font-weight: 700;
  margin: 0; line-height: 1.4; word-break: keep-all;
}

/* 입력 필드 그룹 */
.input-group { text-align: left; margin-bottom: 24px; }
.input-area { margin-bottom: 16px; } 
.label { display: block; font-size: 12px; font-weight: 700; color: #666; margin-bottom: 6px; }
.input {
  width: 100%; padding: 10px 0;
  border: none; border-bottom: 1px solid #ddd;
  font-size: 16px; font-weight: 700; color: #111;
  outline: none; border-radius: 0;
}
.input:focus { border-bottom-color: #111; }
.counter { text-align: right; font-size: 11px; color: #999; margin-top: 4px; }

.btn-confirm {
  width: 100%; padding: 12px;
  background: #e2e2e2;
  border: none; border-radius: 8px;
  font-size: 14px; font-weight: 700;
  color: #666; cursor: pointer;
}
.btn-confirm:hover { background: #d2d2d2; color: #111; }
.btn-confirm:disabled { background: #ccc; cursor: not-allowed; }
</style>