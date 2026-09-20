<template>
  <section class="section product-page">
    <div class="container">
      <div class="page-title-row">
        <div>
          <h1 class="section-title">Danh mục sản phẩm</h1>
          <p class="section-desc">Bộ sưu tập thời trang cao cấp — Dễ dàng lọc theo danh mục, màu sắc, kích cỡ và mức giá.</p>
        </div>
      </div>

      <div class="layout">
        <!-- Cột bên trái: Bộ lọc tìm kiếm -->
        <aside class="panel filters">
          <div class="filter-header">
            <h3>Bộ lọc tìm kiếm</h3>
            <button v-if="hasActiveFilters" class="btn-reset" @click="resetFilters">Xóa bộ lọc</button>
          </div>

          <div class="field">
            <label>Từ khóa tìm kiếm</label>
            <input v-model="filters.q" placeholder="Áo sơ mi, jean, váy..." @keyup.enter="load" />
          </div>

          <div class="field">
            <label>Danh mục sản phẩm</label>
            <select v-model="filters.category_id" @change="load">
              <option value="">Tất cả danh mục</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>

          <div class="field">
            <label>Màu sắc</label>
            <input v-model="filters.color" placeholder="Trắng, đen, xanh..." @keyup.enter="load" />
          </div>

          <div class="field">
            <label>Kích cỡ (Size)</label>
            <input v-model="filters.size" placeholder="S, M, L, XL, 30..." @keyup.enter="load" />
          </div>

          <div class="price-range">
            <div class="field">
              <label>Giá từ (VNĐ)</label>
              <input v-model.number="filters.min_price" type="number" placeholder="100.000" @keyup.enter="load" />
            </div>
            <div class="field">
              <label>Giá đến (VNĐ)</label>
              <input v-model.number="filters.max_price" type="number" placeholder="1.000.000" @keyup.enter="load" />
            </div>
          </div>

          <button class="btn btn-block" @click="load">
            <span>Áp dụng bộ lọc</span>
          </button>
        </aside>

        <!-- Cột bên phải: Lưới sản phẩm & Kết quả -->
        <main class="products-container">
          <div class="results-bar">
            <p class="results-count">
              Tìm thấy <strong>{{ total }}</strong> sản phẩm phù hợp
            </p>
          </div>

          <div v-if="loading" class="loading-panel panel">
            <p>Đang tải danh sách sản phẩm thời trang...</p>
          </div>

          <div v-else-if="items.length > 0" class="grid-products">
            <ProductCard v-for="item in items" :key="item.id" :product="item" />
          </div>

          <div v-else class="empty-panel panel">
            <div class="empty-icon">🔍</div>
            <h3>Không tìm thấy sản phẩm nào!</h3>
            <p class="muted">Hãy thử thay đổi tiêu chí lọc hoặc xóa bộ lọc để xem toàn bộ sản phẩm nhé.</p>
            <button class="btn secondary" @click="resetFilters">Xóa toàn bộ lọc</button>
          </div>
        </main>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductCard from '../components/ProductCard.vue'
import { productApi } from '../services'

const route = useRoute()
const router = useRouter()
const items = ref([])
const total = ref(0)
const categories = ref([])
const loading = ref(false)

const filters = reactive({
  q: '',
  category_id: '',
  color: '',
  size: '',
  min_price: null,
  max_price: null,
})

const hasActiveFilters = computed(() => {
  return Boolean(
    filters.q ||
    filters.category_id ||
    filters.color ||
    filters.size ||
    filters.min_price !== null ||
    filters.max_price !== null
  )
})

async function load() {
  loading.value = true
  try {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value !== '' && value !== null && value !== undefined),
    )
    router.replace({ query: params })
    const { data } = await productApi.list({ ...params, page_size: 30 })
    items.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('Lỗi tải sản phẩm:', error)
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, {
    q: '',
    category_id: '',
    color: '',
    size: '',
    min_price: null,
    max_price: null,
  })
  load()
}

onMounted(async () => {
  Object.assign(filters, {
    q: route.query.q || '',
    category_id: route.query.category_id || '',
    color: route.query.color || '',
    size: route.query.size || '',
    min_price: route.query.min_price ? Number(route.query.min_price) : null,
    max_price: route.query.max_price ? Number(route.query.max_price) : null,
  })
  try {
    const { data } = await productApi.categories()
    categories.value = data || []
  } catch (e) {
    console.error(e)
  }
  await load()
})

watch(
  () => route.query,
  async (newQuery) => {
    const qChanged = newQuery.q !== filters.q
    const catChanged = (newQuery.category_id || '') !== filters.category_id
    if (qChanged || catChanged) {
      filters.q = newQuery.q || ''
      filters.category_id = newQuery.category_id || ''
      await load()
    }
  },
  { deep: true }
)
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  align-items: start;
}

.filters {
  position: sticky;
  top: 130px;
  background: #ffffff;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--line);
}

.filter-header h3 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.4rem;
}

.btn-reset {
  border: none;
  background: transparent;
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.price-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
}

.btn-block {
  width: 100%;
  margin-top: 0.5rem;
}

.results-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
}

.results-count {
  margin: 0;
  color: var(--muted);
  font-size: 0.95rem;
}

.results-count strong {
  color: var(--ink);
}

.loading-panel,
.empty-panel {
  text-align: center;
  padding: 3rem 1.5rem;
  background: #ffffff;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
}

.empty-panel h3 {
  margin: 0 0 0.5rem;
  font-size: 1.3rem;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .filters {
    position: static;
  }
}
</style>
