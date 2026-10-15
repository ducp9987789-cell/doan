<template>
  <div class="admin-datatable-wrapper">
    <!-- Thanh công cụ phía trên bảng: Nút Xóa bộ lọc bên trái + Nút Tải lại bên phải (chỗ ghi hiển thị bản ghi cũ) -->
    <div class="datatable-toolbar">
      <div class="toolbar-left">
        <button v-if="hasActiveFilters" class="btn-clear-filters" @click="clearAllFilters">
          ✕ Xóa tất cả bộ lọc
        </button>
      </div>

      <div class="toolbar-right">
        <slot name="toolbar-actions" />
        <button
          v-if="showReload"
          type="button"
          class="btn-table-reload"
          @click="$emit('reload')"
          :disabled="loading"
          title="Tải lại danh sách"
        >
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" :class="{ 'spin-icon': loading }">
            <path d="M23 4v6h-6M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          <span>Tải lại</span>
        </button>
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
                <!-- Searchable Select / Combobox: vừa có dropdown vừa có tìm kiếm -->
                <div
                  v-if="col.filterType === 'searchable-select'"
                  class="col-filter-combobox"
                  :class="{ 'is-open': activeDropdownKey === col.key }"
                >
                  <div class="combobox-input-wrapper">
                    <input
                      v-model="columnFilters[col.key]"
                      type="text"
                      :placeholder="`Lọc ${col.label}...`"
                      class="col-filter-input combobox-input"
                      @focus="openDropdown(col.key)"
                      @input="openDropdown(col.key)"
                      @keydown.esc="closeDropdown"
                    />
                    <button
                      type="button"
                      class="btn-combobox-toggle"
                      @click.stop="toggleDropdown(col.key)"
                      :title="`Chọn ${col.label}`"
                    >
                      <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </button>
                  </div>

                  <!-- Dropdown popover list -->
                  <div v-if="activeDropdownKey === col.key" class="combobox-menu">
                    <div
                      class="combobox-option"
                      :class="{ active: !columnFilters[col.key] }"
                      @mousedown.prevent="selectComboboxOption(col.key, '')"
                    >
                      <span>Tất cả</span>
                    </div>
                    <div
                      v-for="opt in getFilteredOptions(col)"
                      :key="opt.value !== undefined ? opt.value : opt"
                      class="combobox-option"
                      :class="{ active: columnFilters[col.key] === (opt.value !== undefined ? opt.value : opt) }"
                      @mousedown.prevent="selectComboboxOption(col.key, opt.value !== undefined ? opt.value : opt)"
                    >
                      <span>{{ opt.label || opt }}</span>
                    </div>
                    <div v-if="getFilteredOptions(col).length === 0" class="combobox-no-options">
                      Không có lựa chọn phù hợp
                    </div>
                  </div>
                </div>

                <!-- Dropdown filter thông thường -->
                <select
                  v-else-if="col.filterType === 'select'"
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

                <!-- Text filter thông thường -->
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

    <!-- Phân trang (Pagination) ở đáy bảng - luôn hiển thị -->
    <div class="datatable-pagination">
      <!-- Góc dưới bên trái: Số dòng/trang + Hiển thị X / Y bản ghi -->
      <div class="pagination-left">
        <div class="page-size-selector">
          <span>Số dòng/trang:</span>
          <select v-model="perPage" class="select-per-page">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>

        <span class="rows-info">
          Hiển thị <strong>{{ paginatedRows.length }}</strong> / <strong>{{ filteredRows.length }}</strong> bản ghi
        </span>
      </div>

      <!-- Góc dưới bên phải: Điều hướng phân trang (chỉ hiện khi có nhiều hơn 1 trang) -->
      <div class="pagination-controls" v-if="totalPages > 1">
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
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  showReload: { type: Boolean, default: true },
  emptyText: { type: String, default: 'Chưa có bản ghi nào' },
  defaultSortKey: { type: String, default: '' },
  defaultSortOrder: { type: String, default: 'desc' },
})

defineEmits(['reload'])

const columnFilters = reactive({})
const sortKey = ref(props.defaultSortKey)
const sortOrder = ref(props.defaultSortOrder)
const currentPage = ref(1)
const perPage = ref(10)
const activeDropdownKey = ref(null)

// Initialize column filters
props.columns.forEach((col) => {
  columnFilters[col.key] = ''
})

const hasActiveFilters = computed(() => {
  return Object.values(columnFilters).some((val) => val !== '' && val !== null && val !== undefined)
})

function clearAllFilters() {
  Object.keys(columnFilters).forEach((k) => {
    columnFilters[k] = ''
  })
  activeDropdownKey.value = null
  currentPage.value = 1
}

function toggleDropdown(key) {
  if (activeDropdownKey.value === key) {
    activeDropdownKey.value = null
  } else {
    activeDropdownKey.value = key
  }
}

function openDropdown(key) {
  activeDropdownKey.value = key
}

function closeDropdown() {
  activeDropdownKey.value = null
}

function selectComboboxOption(key, val) {
  columnFilters[key] = val
  activeDropdownKey.value = null
}

function getFilteredOptions(col) {
  const options = col.filterOptions || []
  const filterText = String(columnFilters[col.key] || '').toLowerCase().trim()
  if (!filterText) return options
  return options.filter((opt) => {
    const label = String(opt.label || opt).toLowerCase()
    return label.includes(filterText)
  })
}

function handleClickOutside(e) {
  if (!e.target.closest('.col-filter-combobox')) {
    activeDropdownKey.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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

watch(columnFilters, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.admin-datatable-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

/* Toolbar */
.datatable-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  min-height: 38px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-left: auto;
}

.btn-table-reload {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.9rem;
  background: #ffffff;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-table-reload:hover:not(:disabled) {
  background: #f4f6f8;
  border-color: var(--accent);
  color: var(--accent);
}

.btn-table-reload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 0.8s linear infinite;
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

/* Table */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #ffffff;
  box-shadow: var(--shadow-sm);
  min-height: 240px;
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
  position: relative;
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

/* Combobox (vừa có dropdown vừa có tìm kiếm) */
.col-filter-combobox {
  position: relative;
  width: 100%;
}

.combobox-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.combobox-input {
  padding-right: 26px !important;
}

.btn-combobox-toggle {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: color 0.15s ease;
}

.btn-combobox-toggle:hover {
  color: var(--ink);
}

.combobox-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 180px;
  width: 100%;
  max-height: 220px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  z-index: 100;
  padding: 4px;
}

.combobox-option {
  padding: 7px 10px;
  font-size: 0.85rem;
  color: var(--ink);
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background 0.15s ease;
  text-align: left;
}

.combobox-option:hover {
  background: #f3f4f6;
  color: var(--accent);
}

.combobox-option.active {
  background: #eef2ff;
  color: var(--accent);
  font-weight: 600;
}

.combobox-no-options {
  padding: 8px 10px;
  font-size: 0.82rem;
  color: var(--muted);
  text-align: center;
  font-style: italic;
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

/* Pagination ở góc dưới */
.datatable-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--muted);
}

.select-per-page {
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  border: 1px solid var(--line-strong);
  background: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
}

.rows-info {
  font-size: 0.85rem;
  color: var(--muted);
}

.rows-info strong {
  color: var(--ink);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-left: auto;
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
