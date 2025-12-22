<template>
  <div class="page">
    <h1>나의 영화 DNA</h1>


   
  </div>
</template>

<script setup>
import { ref } from 'vue'



</script>

<style scoped>
.page{ padding: 30px; }
.muted{ color: var(--muted); }
.box{ display:flex; gap: 10px; align-items:center; margin-top: 14px; }
.box .input{ width: min(520px, 90vw); }
.result{
  margin-top: 14px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 16px;
  padding: 14px;
}
pre{ margin: 0; white-space: pre-wrap; }
</style>
