<template>
  <div class="admin-datatable-wrapper">
    <!-- Thanh công cụ phía trên bảng: Tìm kiếm tổng quát + Reset lọc -->
    <div class="datatable-toolbar">
      <div class="toolbar-left">
        <div class="quick-search-box">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            v-model="globalSearch"
            type="text"
            placeholder="Tìm kiếm nhanh trong bảng..."
            class="quick-search-input"
          />
        </div>
        <button v-if="hasActiveFilters" class="btn-clear-filters" @click="clearAllFilters">
          ✕ Xóa tất cả bộ lọc
        </button>
      </div>

      <div class="toolbar-right">
        <span class="rows-info">
          Hiển thị <strong>{{ paginatedRows.length }}</strong> / <strong>{{ filteredRows.length }}</strong> bản ghi
        </span>
      </div>
    </div>

    <!-- Bảng dữ liệu có filter từng cột -->
    <div class="table-container">
      <table class="admin-table">
        <thead>
          <!-- Hàng tiêu đề các cột -->
          <tr class="header-row">
            <th
              v-for="col in columns"
              :key="col.key"
              :style="{ width: col.width || 'auto', textAlign: col.align || 'left' }"
              :class="{ sortable: col.sortable }"
              @click="handleSort(col)"
            >
              <div class="th-content" :style="{ justifyContent: col.align === 'right' ? 'flex-end' : col.align === 'center' ? 'center' : 'flex-start' }">
                <span>{{ col.label }}</span>
                <span v-if="col.sortable" class="sort-icon">
                  <span v-if="sortKey === col.key && sortOrder === 'asc'">▲</span>
                  <span v-else-if="sortKey === col.key && sortOrder === 'desc'">▼</span>
                  <span v-else class="sort-neutral">↕</span>
                </span>
              </div>
            </th>
          </tr>

          <!-- Hàng filter từng ô / từng cột -->
          <tr class="filter-row">
            <th v-for="col in columns" :key="`filter-${col.key}`" :style="{ textAlign: col.align || 'left' }">
              <div v-if="col.filterable !== false" class="col-filter-box">
                <!-- Dropdown filter -->
                <select
                  v-if="col.filterType === 'select'"
                  v-model="columnFilters[col.key]"
                  class="col-filter-select"
                >
                  <option value="">Tất cả</option>
                  <option
                    v-for="opt in (col.filterOptions || [])"
                    :key="opt.value !== undefined ? opt.value : opt"
                    :value="opt.value !== undefined ? opt.value : opt"
                  >
                    {{ opt.label || opt }}
                  </option>
                </select>

                <!-- Text filter -->
                <input
                  v-else
                  v-model="columnFilters[col.key]"
                  type="text"
                  :placeholder="`Lọc ${col.label}...`"
                  class="col-filter-input"
                />
              </div>
              <div v-else class="no-filter">-</div>
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Loading State -->
          <tr v-if="loading">
            <td :colspan="columns.length" class="text-center py-6">
              <div class="loading-state">
                <span class="spinner"></span>
                <span>Đang tải dữ liệu...</span>
              </div>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-else-if="paginatedRows.length === 0">
            <td :colspan="columns.length" class="text-center py-6">
              <div class="empty-state">
                <span class="empty-icon">📂</span>
                <p>{{ emptyText || 'Không có dữ liệu phù hợp với bộ lọc.' }}</p>
              </div>
            </td>
          </tr>

          <!-- Dòng dữ liệu -->
          <tr v-else v-for="(row, rIdx) in paginatedRows" :key="row.id || rIdx" class="data-row">
            <td
              v-for="col in columns"
              :key="`${rIdx}-${col.key}`"
              :style="{ textAlign: col.align || 'left' }"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="rIdx">
                {{ formatCellValue(row[col.key], col) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Phân trang (Pagination) -->
    <div class="datatable-pagination" v-if="totalPages > 1">
      <div class="page-size-selector">
        <span>Số dòng/trang:</span>
        <select v-model="perPage">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>

      <div class="pagination-controls">
        <button
          class="btn-page"
          :disabled="currentPage === 1"
          @click="currentPage = Math.max(1, currentPage - 1)"
        >
          ‹ Trước
        </button>

        <span class="page-numbers">
          Trang <strong>{{ currentPage }}</strong> / <strong>{{ totalPages }}</strong>
        </span>

        <button
          class="btn-page"
          :disabled="currentPage === totalPages"
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
        >
          Sau ›
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Chưa có bản ghi nào' },
  defaultSortKey: { type: String, default: '' },
  defaultSortOrder: { type: String, default: 'desc' },
})

const globalSearch = ref('')
const columnFilters = reactive({})
const sortKey = ref(props.defaultSortKey)
const sortOrder = ref(props.defaultSortOrder)
const currentPage = ref(1)
const perPage = ref(10)

// Initialize column filters
props.columns.forEach((col) => {
  columnFilters[col.key] = ''
})

const hasActiveFilters = computed(() => {
  if (globalSearch.value.trim()) return true
  return Object.values(columnFilters).some((val) => val !== '' && val !== null && val !== undefined)
})

function clearAllFilters() {
  globalSearch.value = ''
  Object.keys(columnFilters).forEach((k) => {
    columnFilters[k] = ''
  })
  currentPage.value = 1
}

function handleSort(col) {
  if (!col.sortable) return
  if (sortKey.value === col.key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = col.key
    sortOrder.value = 'asc'
  }
}

function formatCellValue(val, col) {
  if (val === null || val === undefined || val === '') return '—'
  if (col.format === 'currency') {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
  }
  if (col.format === 'date') {
    return val ? new Date(val).toLocaleString('vi-VN') : '—'
  }
  return val
}

const filteredRows = computed(() => {
  let result = [...props.rows]

  // Global search
  const q = globalSearch.value.trim().toLowerCase()
  if (q) {
    result = result.filter((row) => {
      return Object.values(row).some((val) => {
        if (val === null || val === undefined) return false
        if (typeof val === 'object') {
          return JSON.stringify(val).toLowerCase().includes(q)
        }
        return String(val).toLowerCase().includes(q)
      })
    })
  }

  // Per-column filter
  Object.entries(columnFilters).forEach(([key, filterVal]) => {
    if (filterVal === '' || filterVal === null || filterVal === undefined) return
    const strFilter = String(filterVal).toLowerCase().trim()

    result = result.filter((row) => {
      const cellVal = row[key]
      if (cellVal === null || cellVal === undefined) return false
      return String(cellVal).toLowerCase().includes(strFilter)
    })
  })

  // Sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value]
      let valB = b[sortKey.value]

      if (valA === undefined || valA === null) valA = ''
      if (valB === undefined || valB === null) valB = ''

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder.value === 'asc' ? valA - valB : valB - valA
      }

      const cmp = String(valA).localeCompare(String(valB), 'vi')
      return sortOrder.value === 'asc' ? cmp : -cmp
    })
  }

  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredRows.value.length / perPage.value) || 1
})

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredRows.value.slice(start, start + perPage.value)
})

watch([globalSearch, columnFilters], () => {
  currentPage.value = 1
})
</script>

<style scoped>
.admin-datatable-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Toolbar */
.datatable-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.quick-search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #ffffff;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  padding: 0.45rem 1rem;
  box-shadow: var(--shadow-sm);
}

.quick-search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.88rem;
  width: 220px;
}

.btn-clear-filters {
  border: none;
  background: var(--danger-soft);
  color: var(--danger);
  font-weight: 700;
  font-size: 0.78rem;
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-filters:hover {
  background: var(--danger);
  color: #ffffff;
}

.rows-info {
  font-size: 0.85rem;
  color: var(--muted);
}

/* Table */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #ffffff;
  box-shadow: var(--shadow-sm);
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  text-align: left;
}

.header-row th {
  background: #f7f4ed;
  padding: 0.9rem 1rem;
  font-weight: 700;
  color: var(--ink);
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}

.header-row th.sortable {
  cursor: pointer;
  user-select: none;
}

.header-row th.sortable:hover {
  background: #ede6da;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.sort-icon {
  font-size: 0.75rem;
}

.sort-neutral {
  opacity: 0.35;
}

/* Filter Row */
.filter-row th {
  background: #fdfbf7;
  padding: 0.5rem 0.6rem;
  border-bottom: 2px solid var(--line);
}

.col-filter-box {
  width: 100%;
}

.col-filter-input,
.col-filter-select {
  width: 100%;
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  font-size: 0.8rem;
  background: #ffffff;
  outline: none;
  color: var(--ink);
}

.col-filter-input:focus,
.col-filter-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(17, 75, 67, 0.1);
}

.no-filter {
  text-align: center;
  color: var(--muted);
  font-size: 0.8rem;
}

/* Data Rows */
.data-row {
  border-bottom: 1px solid var(--line);
  transition: background 0.2s ease;
}

.data-row:hover {
  background: #faf8f5;
}

.data-row td {
  padding: 0.85rem 1rem;
  vertical-align: middle;
}

/* Pagination */
.datatable-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--muted);
}

.page-size-selector select {
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--line-strong);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.btn-page {
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  border: 1px solid var(--line-strong);
  background: #ffffff;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-page:hover:not(:disabled) {
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  font-size: 0.88rem;
  color: var(--muted);
}

/* States */
.py-6 {
  padding: 3rem 1rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  color: var(--muted);
}

.empty-icon {
  font-size: 2.5rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--line-strong);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
