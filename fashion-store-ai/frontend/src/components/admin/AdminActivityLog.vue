<template>
  <div class="panel activity-log-panel">
    <div class="activity-header">
      <div class="header-left">
        <span class="activity-icon">📜</span>
        <div>
          <h3 class="activity-title">{{ title }}</h3>
          <p class="activity-desc">Ghi nhận các thao tác thêm mới, chỉnh sửa, cập nhật trạng thái gần đây.</p>
        </div>
      </div>

      <div class="header-right" v-if="logs.length > 0">
        <button class="btn-clear-log" @click="$emit('clear')" title="Xóa lịch sử tạm thời">
          🗑️ Xóa lịch sử
        </button>
      </div>
    </div>

    <!-- Danh sách timeline lịch sử -->
    <div v-if="logs.length === 0" class="empty-log">
      <p class="muted">Chưa có hoạt động nào được ghi nhận trong phiên này.</p>
    </div>

    <div v-else class="timeline-list">
      <div v-for="(log, idx) in logs" :key="log.id || idx" class="timeline-item">
        <div class="timeline-dot-wrapper">
          <div class="timeline-dot" :class="log.type || 'info'">
            <span v-if="log.icon">{{ log.icon }}</span>
            <span v-else-if="log.type === 'create'">➕</span>
            <span v-else-if="log.type === 'update'">✏️</span>
            <span v-else-if="log.type === 'delete'">🗑️</span>
            <span v-else-if="log.type === 'status'">🔄</span>
            <span v-else>📌</span>
          </div>
          <div class="timeline-line" v-if="idx < logs.length - 1"></div>
        </div>

        <div class="timeline-content">
          <div class="timeline-title-row">
            <strong class="log-title">{{ log.title }}</strong>
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          </div>
          <p class="log-desc" v-if="log.description">{{ log.description }}</p>
          <div class="log-meta" v-if="log.user">
            <small class="muted">Thực hiện bởi: <strong>{{ log.user }}</strong></small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  logs: { type: Array, default: () => [] },
  title: { type: String, default: 'Lịch sử hoạt động gần đây' },
})

defineEmits(['clear'])

function formatTime(timestamp) {
  if (!timestamp) return 'Vừa xong'
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) return String(timestamp)
  return date.toLocaleString('vi-VN')
}
</script>

<style scoped>
.activity-log-panel {
  background: #ffffff;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  padding: 1.6rem;
  margin-top: 2rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.4rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.activity-icon {
  font-size: 1.6rem;
}

.activity-title {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  color: var(--ink);
}

.activity-desc {
  margin: 0.15rem 0 0;
  font-size: 0.82rem;
  color: var(--muted);
}

.btn-clear-log {
  border: 1px solid var(--line-strong);
  background: #ffffff;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-log:hover {
  background: var(--danger-soft);
  color: var(--danger);
  border-color: var(--danger);
}

.empty-log {
  text-align: center;
  padding: 1.5rem;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline-item {
  display: flex;
  gap: 1.2rem;
  position: relative;
  padding-bottom: 1.4rem;
}

.timeline-dot-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.timeline-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  background: var(--bg);
  border: 2px solid var(--line-strong);
  z-index: 2;
  flex-shrink: 0;
}

.timeline-dot.create {
  background: #e8f5e9;
  border-color: #4caf50;
}

.timeline-dot.update {
  background: #e3f2fd;
  border-color: #2196f3;
}

.timeline-dot.delete {
  background: #ffebee;
  border-color: #f44336;
}

.timeline-dot.status {
  background: #fff8e1;
  border-color: #ff9800;
}

.timeline-line {
  position: absolute;
  top: 32px;
  bottom: 0;
  width: 2px;
  background: var(--line);
}

.timeline-content {
  flex: 1;
  background: #faf8f5;
  border: 1px solid var(--line);
  padding: 0.85rem 1.1rem;
  border-radius: 12px;
}

.timeline-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.log-title {
  font-size: 0.92rem;
  color: var(--ink);
}

.log-time {
  font-size: 0.78rem;
  color: var(--muted);
}

.log-desc {
  margin: 0;
  font-size: 0.85rem;
  color: var(--ink-light);
  line-height: 1.4;
}

.log-meta {
  margin-top: 0.4rem;
  font-size: 0.78rem;
}
</style>
