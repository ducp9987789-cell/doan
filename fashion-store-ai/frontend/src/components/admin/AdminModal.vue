<template>
  <Teleport to="body">
    <div v-if="show" class="admin-modal-backdrop" @click.self="$emit('close')">
      <div class="admin-modal-card panel fade-up" :style="{ maxWidth: maxWidth || '640px' }">
        <div class="modal-header">
          <div class="modal-title-group">
            <span class="modal-icon" v-if="icon">{{ icon }}</span>
            <h3 class="modal-title">{{ title }}</h3>
          </div>
          <button class="btn-close" type="button" @click="$emit('close')" title="Đóng">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <slot></slot>
        </div>

        <div class="modal-footer" v-if="$slots.footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Thông tin' },
  icon: { type: String, default: '' },
  maxWidth: { type: String, default: '640px' },
})

defineEmits(['close'])
</script>

<style scoped>
.admin-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(25, 23, 20, 0.6);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.admin-modal-card {
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--line);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.6rem;
  border-bottom: 1px solid var(--line);
  background: #faf8f5;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.modal-icon {
  font-size: 1.3rem;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: var(--ink);
}

.btn-close {
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--danger-soft);
  color: var(--danger);
}

.modal-body {
  padding: 1.6rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  padding: 1rem 1.6rem;
  border-top: 1px solid var(--line);
  background: #faf8f5;
}
</style>
