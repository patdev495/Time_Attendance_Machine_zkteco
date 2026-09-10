<template>
  <div class="pagination" v-if="totalPages > 1">
    <!-- Prev -->
    <button class="btn-page" :disabled="currentPage <= 1" @click="go(currentPage - 1)">‹ {{ $t('common.prev') }}</button>

    <!-- Always show page 1 -->
    <button class="btn-page" :class="{ active: currentPage === 1 }" @click="go(1)">1</button>

    <!-- Left ellipsis -->
    <span v-if="showLeftDots" class="dots">…</span>

    <!-- Middle pages -->
    <button
      v-for="p in middlePages"
      :key="p"
      class="btn-page"
      :class="{ active: p === currentPage }"
      @click="go(p)"
    >{{ p }}</button>

    <!-- Right ellipsis -->
    <span v-if="showRightDots" class="dots">…</span>

    <!-- Always show last page (if > 1) -->
    <button v-if="totalPages > 1" class="btn-page" :class="{ active: currentPage === totalPages }" @click="go(totalPages)">{{ totalPages }}</button>

    <!-- Next -->
    <button class="btn-page" :disabled="currentPage >= totalPages" @click="go(currentPage + 1)">{{ $t('common.next') }} ›</button>

    <!-- Go to page input -->
    <span class="goto-wrap">
      {{ $t('common.goto') }}
      <input
        type="number"
        class="goto-input"
        :min="1"
        :max="totalPages"
        v-model.number="gotoValue"
        @keyup.enter="goToPage"
        @blur="goToPage"
        placeholder="p"
      />
    </span>

    <span class="page-info">{{ totalCount.toLocaleString() }} {{ $t('common.records') }}</span>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages:  { type: Number, required: true },
  totalCount:  { type: Number, default: 0 }
})
const emit = defineEmits(['change'])

const gotoValue = ref(props.currentPage)
watch(() => props.currentPage, v => { gotoValue.value = v })

function go(p) {
  const clamped = Math.max(1, Math.min(props.totalPages, p))
  if (clamped !== props.currentPage) emit('change', clamped)
}
function goToPage() {
  if (gotoValue.value) go(gotoValue.value)
}

const middlePages = computed(() => {
  const pages = []
  const start = Math.max(2, props.currentPage - 2)
  const end   = Math.min(props.totalPages - 1, props.currentPage + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const showLeftDots  = computed(() => middlePages.value.length > 0 && middlePages.value[0] > 2)
const showRightDots = computed(() => {
  const m = middlePages.value
  return m.length > 0 && m[m.length - 1] < props.totalPages - 1
})
</script>

<style scoped>
.pagination { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; justify-content: center; padding: 20px 0 10px; }
.btn-page {
  padding: 6px 11px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-family: var(--font-data);
  font-size: 0.82rem;
  transition: all 0.18s;
  min-width: 32px;
}
.btn-page:hover:not(:disabled) { border-color: var(--amber); color: var(--amber); background: var(--amber-glow); }
.btn-page.active { background: var(--amber-dim); color: var(--amber); border-color: rgba(245,166,35,0.4); font-weight: 600; }
.btn-page:disabled { opacity: 0.35; cursor: not-allowed; }
.dots { color: var(--text-muted); padding: 0 2px; }
.goto-wrap { display: flex; align-items: center; gap: 6px; font-size: 0.83rem; color: var(--text-muted); margin-left: 8px; }
.goto-input {
  width: 48px; padding: 5px 7px;
  border-radius: 5px; border: 1px solid var(--border);
  background: var(--bg-input); color: var(--text-main);
  font-family: var(--font-data); font-size: 0.8rem;
  text-align: center;
}
.goto-input:focus { outline: none; border-color: var(--border-focus); box-shadow: 0 0 0 3px rgba(245,166,35,0.1); }
.page-info { font-size: 0.78rem; color: var(--text-muted); margin-left: 8px; font-family: var(--font-data); }
</style>
