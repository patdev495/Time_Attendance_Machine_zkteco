<template>
  <Transition name="fade-backdrop">
    <div v-if="store.confirmState.isOpen" class="modal-backdrop" @click="store.resolveConfirm(false)">
      <Transition name="scale-modal" appear>
        <div class="modal-card" @click.stop>
          <div class="modal-header">
            <div class="warning-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
            <h3>{{ store.confirmState.title }}</h3>
          </div>
          <div class="modal-body">
            <p>{{ store.confirmState.message }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="store.resolveConfirm(false)">{{ $t('common.cancel') }}</button>
            <button class="btn btn-danger" @click="store.resolveConfirm(true)">{{ $t('common.confirm') }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notification.js'
const store = useNotificationStore()
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  width: 100%;
  max-width: 380px;
  overflow: hidden;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.7);
}

.modal-header {
  padding: 24px 24px 16px;
  text-align: center;
}

.warning-icon {
  width: 50px;
  height: 50px;
  background: var(--danger-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--status-dead);
  margin: 0 auto 14px;
}

.modal-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
  margin: 0;
  font-family: var(--font-ui);
}

.modal-body {
  padding: 0 24px 24px;
  text-align: center;
}

.modal-body p {
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
  font-family: var(--font-ui);
}

.modal-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 16px 20px 20px;
  background: var(--bg-raised);
}

.btn {
  padding: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 12px;
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border);
}

.btn-ghost:hover {
  background: var(--amber-glow);
  color: var(--text-main);
  border-color: var(--border-hover);
}

/* Transitions */
.fade-backdrop-enter-active, .fade-backdrop-leave-active { transition: opacity 0.3s ease; }
.fade-backdrop-enter-from, .fade-backdrop-leave-to { opacity: 0; }

.scale-modal-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.scale-modal-leave-active { transition: all 0.2s ease-in; }
.scale-modal-enter-from { opacity: 0; transform: scale(0.9) translateY(20px); }
.scale-modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>
