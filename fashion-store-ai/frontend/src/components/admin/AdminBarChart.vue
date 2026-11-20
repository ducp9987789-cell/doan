<template>
  <div class="admin-bar-chart">
    <div class="chart-header">
      <div class="chart-title-wrap">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="chart-subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-date-picker">
        <label>
          Từ
          <input type="date" :value="dateFrom" @change="onFromChange" />
        </label>
        <label>
          Đến
          <input type="date" :value="dateTo" @change="onToChange" />
        </label>
      </div>
    </div>

    <div v-if="!points.length" class="chart-empty">Chưa có dữ liệu trong khoảng ngày đã chọn.</div>
    <div v-else class="chart-body">
      <div class="y-axis">
        <span>{{ formatValue(maxValue) }}</span>
        <span>{{ formatValue(maxValue / 2) }}</span>
        <span>0</span>
      </div>
      <div class="bars-area">
        <div
          v-for="point in points"
          :key="point.label"
          class="bar-col"
          :title="`${point.label}: ${formatValue(point.value)}`"
        >
          <div class="bar-track">
            <div class="bar-fill" :style="{ height: barHeight(point.value) }"></div>
          </div>
          <span class="bar-label">{{ shortLabel(point.label) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  dateFrom: { type: String, default: '' },
  dateTo: { type: String, default: '' },
  format: { type: String, default: 'number' }, // number | currency
})

const emit = defineEmits(['update:dateFrom', 'update:dateTo', 'change'])

const points = computed(() =>
  (props.labels || []).map((label, idx) => ({
    label,
    value: Number(props.values?.[idx] || 0),
  })),
)

const maxValue = computed(() => {
  const max = Math.max(...points.value.map((p) => p.value), 0)
  return max > 0 ? max : 1
})

function barHeight(value) {
  return `${Math.max((value / maxValue.value) * 100, value > 0 ? 4 : 0)}%`
}

function shortLabel(label) {
  if (!label) return ''
  const parts = String(label).split('-')
  if (parts.length === 3) return `${parts[2]}/${parts[1]}`
  return label
}

function formatValue(value) {
  const num = Number(value || 0)
  if (props.format === 'currency') {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}tr`
    if (num >= 1_000) return `${Math.round(num / 1_000)}k`
    return new Intl.NumberFormat('vi-VN').format(num)
  }
  return new Intl.NumberFormat('vi-VN').format(num)
}

function onFromChange(e) {
  emit('update:dateFrom', e.target.value)
  emit('change')
}

function onToChange(e) {
  emit('update:dateTo', e.target.value)
  emit('change')
}
</script>

<style scoped>
.admin-bar-chart {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1rem 1.1rem 1.2rem;
  box-shadow: var(--shadow-sm);
  min-height: 280px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.chart-title-wrap h3 {
  margin: 0;
  font-size: 1rem;
}

.chart-subtitle {
  margin: 0.2rem 0 0;
  color: var(--muted);
  font-size: 0.82rem;
}

.chart-date-picker {
  display: flex;
  gap: 0.55rem;
  align-items: center;
  margin-left: auto;
}

.chart-date-picker label {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 600;
}

.chart-date-picker input {
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  padding: 0.35rem 0.45rem;
  font-size: 0.82rem;
  color: var(--ink);
  background: #fff;
}

.chart-empty {
  min-height: 180px;
  display: grid;
  place-items: center;
  color: var(--muted);
  font-size: 0.9rem;
}

.chart-body {
  display: grid;
  grid-template-columns: 52px 1fr;
  gap: 0.6rem;
  min-height: 200px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  font-size: 0.72rem;
  color: var(--muted);
  padding: 0.2rem 0 1.4rem;
}

.bars-area {
  display: flex;
  align-items: flex-end;
  gap: 0.35rem;
  border-left: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 0.2rem 0.2rem 0;
  min-height: 200px;
  overflow-x: auto;
}

.bar-col {
  flex: 1 1 28px;
  min-width: 28px;
  max-width: 54px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-track {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar-fill {
  width: 70%;
  max-width: 28px;
  border-radius: 8px 8px 4px 4px;
  background: linear-gradient(180deg, #2f7a6d 0%, #114b43 100%);
  transition: height 0.25s ease;
}

.bar-label {
  margin-top: 0.35rem;
  font-size: 0.68rem;
  color: var(--muted);
  white-space: nowrap;
}
</style>
