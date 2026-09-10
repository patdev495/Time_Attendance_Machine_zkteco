<template>
  <div class="app-layout">
    <AppSidebar v-if="route.name !== 'meal'" />
    <div class="main-content" :style="route.name === 'meal' ? { padding: 0 } : {}">
      <AppHeader />
      <ToastNotification />
      <ConfirmModal />
      <PromptModal />
      <main :class="route.name === 'meal' ? 'kiosk-main-wrapper' : 'container'">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ToastNotification from '@/components/shared/ToastNotification.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'
import PromptModal from '@/components/shared/PromptModal.vue'

const route = useRoute()
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: all 0.28s var(--ease-snap);
}

.container {
  max-width: 1440px;
  margin: 24px auto;
  padding: 0 36px;
  width: 100%;
  flex: 1;
}

.kiosk-main-wrapper {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Page transition — exposure emerge */
.fade-enter-active {
  animation: emerge 0.3s var(--ease-out) both;
}
.fade-leave-active {
  animation: emerge 0.15s var(--ease-snap) reverse both;
}

@media (max-width: 768px) {
  .container { padding: 0 16px; }
}
</style>
