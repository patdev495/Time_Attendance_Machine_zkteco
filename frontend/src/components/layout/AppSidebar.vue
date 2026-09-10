<template>
  <aside :class="['app-sidebar', ui.sidebarOpen ? 'open' : 'collapsed']">
    <!-- Logo mark — exposure frame -->
    <div class="sidebar-brand" v-show="ui.sidebarOpen">
      <div class="brand-mark">
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
          <rect x="1" y="1" width="20" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="5" y="5" width="12" height="12" rx="1" fill="currentColor" opacity="0.25"/>
          <circle cx="11" cy="11" r="3.5" stroke="currentColor" stroke-width="1.5"/>
          <circle cx="11" cy="11" r="1" fill="currentColor"/>
        </svg>
      </div>
      <span class="brand-name">Attendance</span>
    </div>

    <!-- Toggle button -->
    <button class="toggle-btn" @click="ui.toggleSidebar" :title="ui.sidebarOpen ? 'Thu nhỏ' : 'Mở rộng'">
      <svg v-if="ui.sidebarOpen" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
    </button>

    <nav class="sidebar-nav">
      <!-- Attendance group -->
      <div class="nav-group-label" v-show="ui.sidebarOpen">Dữ liệu</div>

      <router-link
        to="/logs"
        :class="['nav-item', route.path === '/logs' ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('attendance.raw_logs') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path === '/logs' ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
        </div>
        <span class="nav-label">{{ $t('attendance.raw_logs') }}</span>
      </router-link>

      <router-link
        to="/summary"
        :class="['nav-item', route.path === '/summary' ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('attendance.daily_summary') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path === '/summary' ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="m9 16 2 2 4-4"/></svg>
        </div>
        <span class="nav-label">{{ $t('attendance.daily_summary') }}</span>
      </router-link>

      <!-- Divider -->
      <div class="nav-rule"></div>

      <!-- Config group -->
      <div class="nav-group-label" v-show="ui.sidebarOpen">Cấu hình</div>

      <router-link
        to="/machines"
        :class="['nav-item', route.path.startsWith('/machines') ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('nav.machines') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path.startsWith('/machines') ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <span class="nav-label">{{ $t('nav.machines') }}</span>
      </router-link>

      <router-link
        to="/employees"
        :class="['nav-item', route.path.startsWith('/employees') ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('nav.employees') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path.startsWith('/employees') ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <span class="nav-label">{{ $t('nav.employees') }}</span>
      </router-link>

      <router-link
        to="/shifts"
        :class="['nav-item', route.path.startsWith('/shifts') ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('nav.shifts') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path.startsWith('/shifts') ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <span class="nav-label">{{ $t('nav.shifts') }}</span>
      </router-link>

      <!-- Divider -->
      <div class="nav-rule"></div>

      <router-link
        to="/meal"
        :class="['nav-item', route.path === '/meal' ? 'active' : '']"
        :title="!ui.sidebarOpen ? $t('meal.kiosk_title') : ''"
      >
        <div class="nav-icon">
          <span class="indicator-dot" :class="route.path === '/meal' ? 'active' : ''"></span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
        </div>
        <span class="nav-label">{{ $t('meal.kiosk_title') }}</span>
      </router-link>
    </nav>

    <!-- Bottom developer timer indicator -->
    <div class="sidebar-footer" v-show="ui.sidebarOpen">
      <div class="timer-strip">
        <span class="timer-label">SYS</span>
        <span class="timer-clock">{{ currentTime }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUIStore } from '@/stores/ui.js'
import { useRoute } from 'vue-router'

const ui = useUIStore()
const route = useRoute()

// Live clock in footer
const currentTime = ref('')
let clockInterval = null

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
  updateClock()
  clockInterval = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
.app-sidebar {
  width: 220px;
  min-width: 220px;
  max-width: 220px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: min-width 0.28s var(--ease-snap), max-width 0.28s var(--ease-snap);
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 101;
  overflow: hidden;
}

.app-sidebar.collapsed {
  min-width: 58px;
  max-width: 58px;
}

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 18px 12px;
  overflow: hidden;
  white-space: nowrap;
}

.brand-mark {
  color: var(--amber);
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.brand-name {
  font-family: var(--font-data);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* Toggle */
.toggle-btn {
  position: absolute;
  top: 18px;
  right: 14px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 26px;
  height: 26px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  z-index: 10;
}
.toggle-btn:hover {
  background: var(--amber-dim);
  border-color: var(--border-hover);
  color: var(--amber);
}

/* Nav group label */
.nav-group-label {
  font-family: var(--font-ui);
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-dim);
  padding: 0 14px 6px;
  overflow: hidden;
  white-space: nowrap;
}

/* Nav */
.sidebar-nav {
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 9px 6px;
  border-radius: 6px;
  color: #c0a878;  /* brighter muted for readability */
  text-decoration: none;
  transition: all 0.18s var(--ease-snap);
  white-space: nowrap;
  overflow: hidden;
  position: relative;
}

.nav-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 44px;
  flex-shrink: 0;
}

.indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-dim);
  transition: all 0.2s;
  flex-shrink: 0;
}
.indicator-dot.active {
  background: var(--amber);
  box-shadow: 0 0 6px rgba(245,166,35,0.6);
  animation: pulse-amber 2s infinite;
}

.nav-label {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 1;
  transition: opacity 0.2s;
  font-family: var(--font-ui);
}

.collapsed .nav-label { opacity: 0; pointer-events: none; }
.collapsed .nav-group-label { opacity: 0; }

.nav-item:hover {
  background: var(--amber-glow);
  color: #f8f0dc;
}
.nav-item:hover .indicator-dot { background: var(--text-muted); }

.nav-item.active {
  background: var(--amber-dim);
  color: var(--amber);
}
.nav-item.active .indicator-dot {
  background: var(--amber);
  box-shadow: 0 0 6px rgba(245,166,35,0.7);
}

/* Divider */
.nav-rule {
  height: 1px;
  background: var(--border);
  margin: 10px 6px;
}

/* Footer timer strip */
.sidebar-footer {
  padding: 12px 14px 16px;
  border-top: 1px solid var(--border);
  overflow: hidden;
}

.timer-strip {
  display: flex;
  align-items: center;
  gap: 10px;
}

.timer-label {
  font-family: var(--font-data);
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  text-transform: uppercase;
}

.timer-clock {
  font-family: var(--font-data);
  font-size: 0.78rem;
  color: var(--amber);
  letter-spacing: 0.05em;
  opacity: 0.7;
}

/* Mobile */
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    transform: translateX(-100%);
  }
  .app-sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 24px rgba(0,0,0,0.6);
  }
}
</style>
