<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>전체 코멘트 <span class="count">{{ reviews.length }}</span></h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="sort-bar">
        <select class="sort-select" :value="currentSort" @change="$emit('sort', $event.target.value)">
          <option value="likes">좋아요 순</option>
          <option value="latest">최신 순</option>
        </select>
      </div>

      <div class="modal-body list-body">
        <div 
          v-for="review in reviews" 
          :key="review.id" 
          class="comment-item"
          @click="$emit('select', review)"
        >
          <div class="item-header">
            <div class="user">
              <img v-if="review.user.profile_image" :src="review.user.profile_image" class="u-img">
              <div v-else class="u-icon">👤</div>
              <span class="name">{{ review.user.username }}</span>
            </div>
            <div class="movie-info" v-if="review.movie">
                <span class="m-title">{{ review.movie.title }}</span>
                <span class="rating">★ {{ review.rating }}</span>
            </div>
            <div class="rating" v-else>★ {{ review.rating }}</div>
          </div>
          <div class="item-content">{{ review.content }}</div>
          <div class="item-footer">
            <span>👍 {{ review.likes_count }}</span>
            <span>💬 {{ review.comments_count || 0 }}</span>
            <span class="date">{{ formatDate(review.created_at) }}</span>
          </div>
        </div>
        
        <div v-if="reviews.length === 0" class="no-data">
            코멘트가 없습니다.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  reviews: { type: Array, default: () => [] },
  currentSort: { type: String, default: 'latest' } // 기본값 latest
})
defineEmits(['close', 'sort', 'select'])

function formatDate(dateStr) {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.modal-overlay { 
  position: fixed; 
  inset: 0; 
  background: rgba(0, 0, 0, 0.7); /* 오버레이는 가독성을 위해 어두운 톤 유지 */
  z-index: 2000; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  backdrop-filter: blur(4px); /* 배경 흐림 효과 추가 (선택사항) */
}

.modal-content { 
  background: var(--card); /* white -> var(--card) */
  width: 600px; 
  height: 80vh; 
  border-radius: 12px; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  box-shadow: var(--shadow); /* rgba -> var(--shadow) */
  border: 1px solid var(--border); /* 다크모드 대응 테두리 */
}

.modal-header { 
  padding: 16px 20px; 
  border-bottom: 1px solid var(--border); /* #eee -> var(--border) */
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  background: var(--card);
}

.modal-header h3 { 
  margin: 0; 
  font-size: 18px; 
  font-weight: 700; 
  color: var(--text); /* 글자색 대응 */
}

.count { 
  color: var(--primary); /* #ff2f6e -> var(--primary) 포인트 컬러 */
  margin-left: 6px; 
}

.close-btn { 
  background: none; 
  border: none; 
  font-size: 24px; 
  cursor: pointer; 
  color: var(--muted); /* #999 -> var(--muted) */
}

.sort-bar { 
  padding: 10px 20px; 
  border-bottom: 1px solid var(--border); /* #f5f5f5 -> var(--border) */
  background: var(--card); 
  text-align: right; 
}

.sort-select { 
  padding: 6px 10px; 
  border: 1px solid var(--border); /* #ddd -> var(--border) */
  border-radius: 4px; 
  font-size: 13px; 
  background: var(--input-bg); /* 배경 대응 */
  color: var(--text);          /* 글자색 대응 */
  outline: none; 
  cursor: pointer; 
}

.list-body { 
  flex: 1; 
  overflow-y: auto; 
  padding: 20px; 
  background: var(--bg); /* #f8f8f8 -> var(--bg) */
}

.no-data { 
  text-align: center; 
  color: var(--muted); /* #999 -> var(--muted) */
  margin-top: 40px; 
}

/* 개별 아이템 카드 */
.comment-item { 
  background: var(--card); /* white -> var(--card) */
  border-radius: 8px; 
  padding: 16px; 
  margin-bottom: 12px; 
  border: 1px solid var(--border); /* #eee -> var(--border) */
  cursor: pointer; 
  transition: all 0.2s; 
}

.comment-item:hover { 
  border-color: var(--primary); /* #ccc -> var(--primary) 포인트 컬러 */
  box-shadow: var(--shadow); 
}

.item-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 10px; 
  padding-bottom: 8px; 
  border-bottom: 1px solid var(--border); /* #f9f9f9 -> var(--border) */
}

.user { display: flex; align-items: center; gap: 8px; }
.u-img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); }
.u-icon { font-size: 24px; color: var(--muted); }
.name { font-size: 14px; font-weight: 700; color: var(--text); } /* #333 -> var(--text) */

/* 영화 정보 스타일 */
.movie-info { display: flex; align-items: center; gap: 8px; }
.m-title { font-size: 13px; color: var(--muted); font-weight: 600; } /* #666 -> var(--muted) */
.rating { 
  font-size: 13px; 
  background: var(--bg); /* #eee -> var(--bg) */
  color: var(--text);
  padding: 2px 8px; 
  border-radius: 12px; 
  font-weight: 600; 
  border: 1px solid var(--border);
}

.item-content { 
  font-size: 15px; 
  color: var(--text); /* #444 -> var(--text) */
  line-height: 1.5; 
  margin-bottom: 12px; 
  white-space: pre-wrap; 
}

.item-footer { 
  font-size: 13px; 
  color: var(--muted); /* #888 -> var(--muted) */
  display: flex; 
  gap: 16px; 
  align-items: center; 
}

.date { 
  margin-left: auto; 
  font-size: 12px; 
  color: var(--muted); /* #aaa -> var(--muted) */
  opacity: 0.8;
}

@media (max-width: 768px) { 
  .modal-content { width: 100%; height: 100vh; border-radius: 0; border: none; } 
}
</style>