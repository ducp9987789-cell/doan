<template>
  <section class="section">
    <div class="container">
      <h1 class="section-title">Admin</h1>
      <p class="section-desc">Manage products, orders, promotions, FAQ and chatbot knowledge.</p>

      <div class="stats">
        <article class="panel" v-for="(value, key) in summary" :key="key">
          <small class="muted">{{ key }}</small>
          <strong>{{ value }}</strong>
        </article>
      </div>

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <div v-if="activeTab === 'Orders'" class="panel">
        <article v-for="order in orders" :key="order.id" class="row">
          <div>
            <strong>#{{ order.id.slice(-6) }}</strong>
            <p class="muted">{{ order.status }} · {{ formatPrice(order.total) }}</p>
          </div>
          <select :value="order.status" @change="updateStatus(order.id, $event.target.value)">
            <option v-for="status in statuses" :key="status" :value="status">{{ status }}</option>
          </select>
        </article>
      </div>

      <div v-else-if="activeTab === 'Products'" class="panel">
        <form class="grid-form" @submit.prevent="createProduct">
          <input v-model="productForm.name" placeholder="Product name" required />
          <input v-model="productForm.price" type="number" placeholder="Price" required />
          <select v-model="productForm.category_id" required>
            <option disabled value="">Category</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <input v-model="productForm.image" placeholder="Image URL" />
          <textarea v-model="productForm.description" placeholder="Description" required />
          <button class="btn" type="submit">Add product</button>
        </form>
        <article v-for="item in products" :key="item.id" class="row">
          <div>
            <strong>{{ item.name }}</strong>
            <p class="muted">{{ formatPrice(item.price) }} · stock {{ item.stock }}</p>
          </div>
          <button class="btn secondary" @click="removeProduct(item.id)">Delete</button>
        </article>
      </div>

      <div v-else-if="activeTab === 'Promotions'" class="panel">
        <form class="grid-form" @submit.prevent="createPromotion">
          <input v-model="promoForm.code" placeholder="Code" required />
          <input v-model="promoForm.title" placeholder="Title" required />
          <input v-model.number="promoForm.discount_value" type="number" placeholder="Value" required />
          <select v-model="promoForm.discount_type">
            <option value="percent">percent</option>
            <option value="fixed">fixed</option>
          </select>
          <button class="btn" type="submit">Add promotion</button>
        </form>
        <article v-for="promo in promotions" :key="promo.id" class="row">
          <div>
            <strong>{{ promo.code }}</strong>
            <p class="muted">{{ promo.title }}</p>
          </div>
        </article>
      </div>

      <div v-else-if="activeTab === 'FAQ'" class="panel">
        <form class="grid-form" @submit.prevent="createFaq">
          <input v-model="faqForm.question" placeholder="Question" required />
          <textarea v-model="faqForm.answer" placeholder="Answer" required />
          <button class="btn" type="submit">Add FAQ</button>
        </form>
        <article v-for="faq in faqs" :key="faq.id" class="row">
          <div>
            <strong>{{ faq.question }}</strong>
            <p class="muted">{{ faq.answer }}</p>
          </div>
        </article>
      </div>

      <div v-else class="panel">
        <button class="btn" @click="reindex">Reindex chatbot knowledge</button>
        <p class="muted">{{ reindexMessage }}</p>
        <article v-for="log in chatLogs" :key="log.id" class="row">
          <div>
            <strong>{{ log.question }}</strong>
            <p class="muted">{{ log.answer }}</p>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminApi, chatApi, orderApi, productApi } from '../services'

const activeTab = ref('Orders')
const tabs = ['Orders', 'Products', 'Promotions', 'FAQ', 'Chatbot']
const statuses = ['pending', 'confirmed', 'shipping', 'completed', 'cancelled']
const dashboard = ref({})
const orders = ref([])
const products = ref([])
const categories = ref([])
const promotions = ref([])
const faqs = ref([])
const chatLogs = ref([])
const reindexMessage = ref('')

const productForm = reactive({
  name: '',
  price: 199000,
  category_id: '',
  description: '',
  image: '',
})
const promoForm = reactive({
  code: '',
  title: '',
  discount_type: 'percent',
  discount_value: 10,
  min_order_value: 0,
})
const faqForm = reactive({
  question: '',
  answer: '',
  category: 'general',
})

const summary = computed(() => ({
  users: dashboard.value.users || 0,
  products: dashboard.value.products || 0,
  orders: dashboard.value.orders || 0,
  revenue: formatPrice(dashboard.value.revenue || 0),
}))

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

async function refresh() {
  const [dash, orderRes, productRes, categoryRes, promoRes, faqRes, logRes] = await Promise.all([
    adminApi.dashboard(),
    orderApi.adminOrders(),
    adminApi.products({ page_size: 50 }),
    productApi.categories(),
    productApi.promotions({ active_only: false }),
    chatApi.faqs(),
    chatApi.chatLogs(),
  ])
  dashboard.value = dash.data
  orders.value = orderRes.data
  products.value = productRes.data.items
  categories.value = categoryRes.data
  promotions.value = promoRes.data
  faqs.value = faqRes.data
  chatLogs.value = logRes.data
  if (!productForm.category_id && categories.value[0]) {
    productForm.category_id = categories.value[0].id
  }
}

async function updateStatus(id, status) {
  await orderApi.updateOrderStatus(id, status)
  await refresh()
}

async function createProduct() {
  await productApi.create({
    name: productForm.name,
    price: Number(productForm.price),
    category_id: productForm.category_id,
    description: productForm.description,
    images: productForm.image ? [productForm.image] : [],
    colors: ['Đen'],
    sizes: ['M', 'L'],
    stock: 20,
    is_featured: false,
  })
  Object.assign(productForm, { name: '', description: '', image: '', price: 199000 })
  await refresh()
}

async function removeProduct(id) {
  await productApi.remove(id)
  await refresh()
}

async function createPromotion() {
  await productApi.createPromotion({ ...promoForm })
  Object.assign(promoForm, { code: '', title: '', discount_value: 10 })
  await refresh()
}

async function createFaq() {
  await chatApi.createFaq({ ...faqForm })
  Object.assign(faqForm, { question: '', answer: '' })
  await refresh()
}

async function reindex() {
  const { data } = await chatApi.reindex()
  reindexMessage.value = `Indexed ${data.indexed_documents} documents`
}

onMounted(refresh)
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.8rem;
  margin-bottom: 1.4rem;
}

.stats strong {
  display: block;
  margin-top: 0.35rem;
  font-size: 1.35rem;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tabs button {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  padding: 0.55rem 0.95rem;
  cursor: pointer;
}

.tabs button.active {
  background: var(--accent);
  color: white;
  border-color: transparent;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--line);
}

.grid-form {
  display: grid;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.grid-form input,
.grid-form select,
.grid-form textarea {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  background: rgba(255, 255, 255, 0.75);
}
</style>
