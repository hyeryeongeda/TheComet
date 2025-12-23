<template>
  <section class="sub-section">
    <div class="head-row">
      <h3 class="sub-title">코멘트 <span class="cnt">{{ reviews.length }}+</span></h3>
      <span class="more-link" @click="$emit('open-list-modal')">더보기 ></span>
    </div>

    <div v-if="reviews.length === 0" class="no-data">아직 코멘트가 없습니다.</div>
    
    <div v-else class="comment-grid">
      <ReviewCard
        v-for="review in reviews.slice(0, 6)" 
        :key="review.id" 
        :review="review"
        @click="$emit('open-detail-modal', review)"
      />
    </div>
  </section>
</template>

<script setup>
import ReviewCard from '@/components/review/ReviewCard.vue'

// 부모(MovieDetailView)로부터 전달받는 데이터
defineProps({
  reviews: {
    type: Array,
    required: true
  }
})

// 부모에게 전달할 이벤트 정의
defineEmits(['open-list-modal', 'open-detail-modal'])
</script>

<style scoped>
.head-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.sub-title { font-size: 20px; font-weight: 800; color: #000; }
.cnt { color: #ff2f6e; margin-left: 4px; }
.more-link { font-size: 14px; color: #ff2f6e; cursor: pointer; font-weight: 700; }
.no-data { color: #999; font-size: 14px; padding: 40px 0; text-align: center; }

/* 홈 화면의 review-grid와 동일한 설정 */
.comment-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 상세페이지는 공간상 2열이 적당합니다 */
  gap: 16px;
}

@media (max-width: 640px) {
  .comment-grid { grid-template-columns: 1fr; }
}
</style>