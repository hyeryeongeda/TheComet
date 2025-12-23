<template>
  <div class="auth-card">
    <div class="brand">
      <img class="logo" :src="logoSrc" alt="혜성 로고" />
      <div class="brand-text">
        <h1>혜성</h1>
        <p v-if="title" class="subtitle">{{ title }}</p>
      </div>
    </div>

    <slot />

    <div v-if="showFooter" class="footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineProps({
  title: { type: String, default: '' },
  showFooter: { type: Boolean, default: true },
})

const logoSrc = computed(() => new URL('@/assets/comet_logo.png', import.meta.url).href)
</script>

<style scoped src="./login.css"></style>
<style scoped>
.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.subtitle {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
}
</style>
