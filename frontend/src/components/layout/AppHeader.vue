<template>
  <header class="site-header" v-if="route.name !== 'meal'">
    <div class="header-left">
      <a href="#" class="site-title" @click.prevent="goHome">{{ $t('nav.title') }}</a>
      <p class="tagline">{{ $t('layout.tagline') }}</p>
    </div>
    <nav class="header-actions">
      <!-- Language Switcher -->
      <div class="lang-switcher-wrap">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted)"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        <select v-model="currentLang" @change="changeLanguage" id="langSwitcher" name="lang" class="lang-select">
          <option value="vi">🇻🇳 Tiếng Việt</option>
          <option value="en">🇬🇧 English</option>
          <option value="zh">🇨🇳 中文</option>
        </select>
      </div>

      <button class="settings-trigger" @click="openMachineSettings" title="Cấu hình máy chấm công">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        <span>Máy</span>
      </button>
    </nav>
  </header>

  <!-- Machine Settings Modal -->
  <teleport to="body">
    <div v-if="showMachineSettings" class="modal-overlay-global" @click.self="showMachineSettings = false">
      <div class="modal-content-global machine-settings-modal">
        <div class="modal-header-global">
          <div class="modal-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <h3>{{ $t('meal.machine_settings') || 'Cấu hình máy chấm công' }}</h3>
          </div>
          <button class="close-btn-global" @click="showMachineSettings = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="modal-body-global">
          <div class="machine-config-list">
            <div v-for="m in allMachineConfigs" :key="m.ip" class="machine-config-item">
              <div class="m-info-col">
                <div class="m-ip-row">
                  <span class="m-status-dot" :class="getMachineStatusClass(m.ip)"></span>
                  <span class="m-ip">{{ m.ip }}</span>
                </div>
                <div v-if="machineStatus[m.ip] && machineStatus[m.ip].last_real_event" class="m-last-activity">
                  {{ $t('meal.last_event') }} {{ formatLastEventTime(machineStatus[m.ip].last_real_event) }}
                </div>
                <div v-else-if="machineStatus[m.ip] && m.is_live" class="m-last-activity no-activity">
                  {{ $t('meal.no_event') }}
                </div>
              </div>
              <div class="m-toggles">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="m.is_live" @change="toggleMachineConfig(m)">
                  <span class="slider"></span>
                  <span class="toggle-label">Live</span>
                </label>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="m.is_canteen" @change="toggleMachineConfig(m)">
                  <span class="slider"></span>
                  <span class="toggle-label">{{ $t('meal.toggle_canteen') || 'Canteen' }}</span>
                </label>
                <button
                  v-if="m.is_live"
                  class="btn btn-reconnect-small"
                  @click="handleReconnect(m.ip)"
                  :disabled="reconnectingIps.includes(m.ip)"
                  :title="$t('meal.reconnect_title') + ' ' + m.ip"
                >
                  <svg v-if="!reconnectingIps.includes(m.ip)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                  <span class="spin-sm" v-else></span>
                  {{ reconnectingIps.includes(m.ip) ? '...' : $t('meal.reconnect_btn') }}
                </button>
              </div>
            </div>
          </div>
          <div class="modal-note">
            {{ $t('meal.config_note') || '* Thay đổi sẽ được hệ thống cập nhật sau tối đa 10 giây.' }}
          </div>
        </div>
      </div>
    </div>
  </teleport>

  <!-- Status banners -->
  <div v-if="syncStore.syncRunning" class="status-banner sync-banner">
    <div class="banner-inner">
      <span class="banner-pulse"></span>
      {{ syncStore.syncMessage }}
    </div>
  </div>
  <div v-if="syncStore.deleteRunning" class="status-banner delete-banner">
    <div class="banner-inner">{{ syncStore.deleteMessage }}</div>
  </div>

  <!-- Export Progress Banner -->
  <div v-if="exportStore.isRunning || exportStore.error" class="status-banner" :class="exportStore.error ? 'delete-banner' : 'sync-banner'">
    <div v-if="exportStore.error" class="banner-inner">{{ exportStore.error }}</div>
    <div v-else class="export-banner-content">
      <div class="progress-container">
        <div class="progress-fill" :style="{ width: exportStore.progress + '%' }"></div>
      </div>
      <span>{{ $t('export.progress_label') || 'Export' }}: {{ exportStore.currentStep }} ({{ exportStore.progress }}%)</span>
    </div>
  </div>

  <!-- Excel Sync Progress Banner -->
  <div v-if="syncStore.excelSyncRunning || syncStore.excelSyncError" class="status-banner teal-banner">
    <div v-if="syncStore.excelSyncError" class="banner-inner" style="color: var(--status-dead);">{{ syncStore.excelSyncError }}</div>
    <div v-else class="export-banner-content">
      <div class="progress-container">
        <div class="progress-fill teal-fill" :style="{ width: syncStore.excelSyncProgress + '%' }"></div>
      </div>
      <span style="color: #f5a623;">{{ $t('sync.progress_label') || 'Sync' }}: {{ syncStore.excelSyncStep }} ({{ syncStore.excelSyncProgress }}%)</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, watch } from 'vue'
import { getLiveStatus, reconnectMachine } from '@/features/machines/api.js'
import { useSyncStore } from '@/stores/sync.js'
import { useExportStore } from '@/stores/export.js'
import { useAttendanceStore } from '@/stores/attendance.js'
import { useI18n } from 'vue-i18n'
import { setLanguage } from '@/i18n/index.js'
import { useRouter, useRoute } from 'vue-router'
import { mealApi } from '@/features/meal_tracking/api.js'

const syncStore = useSyncStore()
const exportStore = useExportStore()
const attendanceStore = useAttendanceStore()
const router = useRouter()
const route = useRoute()

const { locale } = useI18n()
const currentLang = ref(locale.value)

function changeLanguage() {
  setLanguage(currentLang.value)
}

function goHome() {
  router.push('/logs')
}

const showMachineSettings = ref(false)
const allMachineConfigs = ref([])
const machineStatus = ref({})
const reconnectingIps = ref([])
let statusInterval = null

async function fetchLiveStatus() {
  try {
    const data = await getLiveStatus()
    machineStatus.value = data || {}
  } catch (e) {
    console.error('Error fetching machine status:', e)
  }
}

function getMachineStatusClass(ip) {
  const m = machineStatus.value[ip]
  if (!m) return 'off'
  const status = typeof m === 'object' ? m.status : m
  if (status === 'connected') return 'live'
  if (status === 'stuck') return 'warn'
  if (status === 'disconnected') return 'dead'
  return 'off'
}

async function handleReconnect(ip) {
  reconnectingIps.value.push(ip)
  try {
    const res = await reconnectMachine(ip)
    console.log(`Reconnected machine ${ip}:`, res.message)
    await fetchLiveStatus()
  } catch (e) {
    console.error(`Failed to reconnect machine ${ip}:`, e)
    alert(`Không thể kết nối lại máy ${ip}: ${e.message}`)
  } finally {
    reconnectingIps.value = reconnectingIps.value.filter(item => item !== ip)
  }
}

function formatLastEventTime(timestamp) {
  if (!timestamp) return ''
  const d = new Date(timestamp * 1000)
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

watch(showMachineSettings, (newVal) => {
  if (!newVal && statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
})

async function openMachineSettings() {
  try {
    const { data } = await mealApi.getAllMachineConfigs()
    if (!data || data.length === 0) {
      alert('Không tìm thấy danh sách máy hoặc tệp cấu hình trống.')
    }
    allMachineConfigs.value = data
    showMachineSettings.value = true
    fetchLiveStatus()
    if (statusInterval) clearInterval(statusInterval)
    statusInterval = setInterval(fetchLiveStatus, 10000)
  } catch (e) {
    console.error('Error fetching machine configs:', e)
    alert('Không thể kết nối đến máy chủ: ' + (e.response?.data?.detail || e.message))
  }
}

async function toggleMachineConfig(machine) {
  try {
    await mealApi.updateMachineConfig(machine.ip, {
      is_live: machine.is_live,
      is_canteen: machine.is_canteen
    })
  } catch (e) {
    console.error('Error updating machine config:', e)
    alert('Lỗi khi cập nhật cấu hình máy')
    openMachineSettings()
  }
}
</script>

<style scoped>
/* ─── Header ─── */
.site-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-sidebar);
}

.site-title {
  font-family: var(--font-data);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
  text-decoration: none;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: color 0.2s;
}
.site-title:hover { color: var(--amber); }

.tagline {
  font-family: var(--font-ui);
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 2px;
  letter-spacing: 0.04em;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Lang switcher */
.lang-switcher-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
}

.lang-select {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.82rem;
  outline: none;
  padding: 0;
  padding-right: 20px;
  width: auto;
  cursor: pointer;
  font-family: var(--font-ui);
}
.lang-select:focus { box-shadow: none; }

/* Settings button */
.settings-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 7px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  font-family: var(--font-ui);
  font-weight: 500;
  transition: all 0.2s;
}
.settings-trigger:hover {
  background: var(--amber-glow);
  border-color: var(--border-hover);
  color: var(--amber);
}

/* ─── Status Banners ─── */
.status-banner {
  padding: 7px 28px;
  font-size: 0.82rem;
  font-family: var(--font-data);
}

.banner-inner {
  display: flex;
  align-items: center;
  gap: 10px;
}

.banner-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--amber);
  animation: pulse-amber 1.5s infinite;
  flex-shrink: 0;
}

.sync-banner {
  background: rgba(245,166,35,0.06);
  border-bottom: 1px solid rgba(245,166,35,0.2);
  color: var(--amber);
}
.delete-banner {
  background: rgba(255,68,68,0.07);
  border-bottom: 1px solid rgba(255,68,68,0.2);
  color: #ff7777;
}
.teal-banner {
  background: rgba(57,255,110,0.05);
  border-bottom: 1px solid rgba(57,255,110,0.15);
}

.export-banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  max-width: 600px;
  margin: 0 auto;
}
.progress-container {
  flex: 1;
  height: 4px;
  background: rgba(255,172,30,0.1);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--amber);
  transition: width 0.3s ease;
}
.teal-fill { background: var(--status-live); }

/* ─── Modal ─── */
.modal-overlay-global {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content-global {
  width: 620px;
  max-width: 95vw;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header-global {
  padding: 14px 18px;
  background: var(--bg-raised);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--amber);
}

.modal-header-global h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-main);
  font-family: var(--font-ui);
}

.close-btn-global {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 28px;
  height: 28px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.close-btn-global:hover {
  background: var(--danger-light);
  color: #ff7777;
  border-color: rgba(255,68,68,0.3);
}

.machine-config-list {
  padding: 16px;
  max-height: 55vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.machine-config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: 7px;
  transition: border-color 0.15s;
}
.machine-config-item:hover { border-color: var(--border-hover); }

.m-info-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.m-ip-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.m-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.m-status-dot.live { background: var(--status-live); box-shadow: 0 0 5px var(--status-live); }
.m-status-dot.warn { background: var(--status-warn); box-shadow: 0 0 5px var(--status-warn); }
.m-status-dot.dead { background: var(--status-dead); box-shadow: 0 0 5px var(--status-dead); }
.m-status-dot.off  { background: var(--text-dim); }

.m-ip {
  font-family: var(--font-data);
  color: var(--amber);
  font-weight: 600;
  font-size: 0.9rem;
}

.m-last-activity {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-data);
}
.m-last-activity.no-activity { color: #c8902a; }

.m-toggles {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Toggle switch */
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
}
.toggle-switch input { display: none; }
.slider {
  position: relative;
  width: 32px;
  height: 17px;
  background: #2a2000;
  border-radius: 17px;
  border: 1px solid var(--border);
  transition: 0.25s;
}
.slider::before {
  content: '';
  position: absolute;
  width: 11px;
  height: 11px;
  left: 2px;
  bottom: 2px;
  background: var(--text-dim);
  border-radius: 50%;
  transition: 0.25s;
}
.toggle-switch input:checked + .slider {
  background: rgba(57,255,110,0.15);
  border-color: rgba(57,255,110,0.3);
}
.toggle-switch input:checked + .slider::before {
  transform: translateX(15px);
  background: var(--status-live);
  box-shadow: 0 0 5px var(--status-live);
}
.toggle-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-ui);
}
.toggle-switch input:checked ~ .toggle-label { color: var(--status-live); }

/* Reconnect btn */
.btn-reconnect-small {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: rgba(245,166,35,0.08);
  border: 1px solid rgba(245,166,35,0.2);
  color: var(--amber);
  font-size: 0.75rem;
  font-weight: 500;
  font-family: var(--font-ui);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-reconnect-small:hover:not(:disabled) {
  background: rgba(245,166,35,0.15);
  border-color: rgba(245,166,35,0.4);
}
.btn-reconnect-small:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.spin-sm {
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(245,166,35,0.3);
  border-top-color: var(--amber);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.modal-note {
  padding: 10px 16px;
  font-size: 0.72rem;
  color: var(--text-dim);
  font-style: italic;
  border-top: 1px solid var(--border);
  font-family: var(--font-ui);
}
</style>
