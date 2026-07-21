<template>
  <section class="section">
    <div class="container">
      <h1 class="section-title">Products</h1>
      <p class="section-desc">Filter by category, color, size and price.</p>

      <div class="layout">
        <aside class="panel filters">
          <div class="field">
            <label>Search</label>
            <input v-model="filters.q" placeholder="Shirt, dress, denim..." @keyup.enter="load" />
          </div>
          <div class="field">
            <label>Category</label>
            <select v-model="filters.category_id">
              <option value="">All</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="field">
            <label>Color</label>
            <input v-model="filters.color" placeholder="Black, white..." />
          </div>
          <div class="field">
            <label>Size</label>
            <input v-model="filters.size" placeholder="M, L, 30..." />
          </div>
          <div class="field">
            <label>Min price</label>
            <input v-model.number="filters.min_price" type="number" />
          </div>
          <div class="field">
            <label>Max price</label>
            <input v-model.number="filters.max_price" type="number" />
          </div>
          <button class="btn" @click="load">Apply filters</button>
        </aside>

        <div>
          <p class="muted">{{ total }} products</p>
          <div class="grid-products">
            <ProductCard v-for="item in items" :key="item.id" :product="item" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductCard from '../components/ProductCard.vue'
import { productApi } from '../services'

const route = useRoute()
const router = useRouter()
const items = ref([])
const total = ref(0)
const categories = ref([])
const filters = reactive({
  q: '',
  category_id: '',
  color: '',
  size: '',
  min_price: null,
  max_price: null,
})

async function load() {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== '' && value !== null && value !== undefined),
  )
  router.replace({ query: params })
  const { data } = await productApi.list(params)
  items.value = data.items
  total.value = data.total
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
  const { data } = await productApi.categories()
  categories.value = data
  await load()
})

watch(
  () => route.query.category_id,
  async (value) => {
    if (value !== filters.category_id) {
      filters.category_id = value || ''
      await load()
    }
  },
)
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
