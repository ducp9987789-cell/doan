<template>
  <section class="section" v-if="product">
    <div class="container detail">
      <img :src="product.images?.[0]" :alt="product.name" class="media fade-up" />
      <div class="info fade-up">
        <p class="muted">{{ product.category_name }}</p>
        <h1>{{ product.name }}</h1>
        <div class="price">
          <span class="sale">{{ formatPrice(product.sale_price || product.price) }}</span>
          <span v-if="product.sale_price" class="old">{{ formatPrice(product.price) }}</span>
        </div>
        <p>{{ product.description }}</p>

        <div class="field">
          <label>Color</label>
          <select v-model="color">
            <option v-for="item in product.colors" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="field">
          <label>Size</label>
          <select v-model="size">
            <option v-for="item in product.sizes" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="field">
          <label>Quantity</label>
          <input v-model.number="quantity" type="number" min="1" />
        </div>

        <button class="btn" :disabled="adding" @click="addToCart">
          {{ adding ? 'Adding...' : 'Add to cart' }}
        </button>
        <p v-if="message" class="muted">{{ message }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../services'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()

const product = ref(null)
const color = ref('')
const size = ref('')
const quantity = ref(1)
const adding = ref(false)
const message = ref('')

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

async function addToCart() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  adding.value = true
  message.value = ''
  try {
    await cart.addItem({
      product_id: product.value.id,
      quantity: quantity.value,
      color: color.value,
      size: size.value,
    })
    message.value = 'Added to cart'
  } catch (error) {
    message.value = error.response?.data?.detail || 'Could not add to cart'
  } finally {
    adding.value = false
  }
}

onMounted(async () => {
  const { data } = await productApi.get(route.params.id)
  product.value = data
  color.value = data.colors?.[0] || ''
  size.value = data.sizes?.[0] || ''
})
</script>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 2rem;
  align-items: start;
}

.media {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  background: var(--bg-deep);
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 5vw, 3.8rem);
  margin: 0.2rem 0 0.8rem;
}

@media (max-width: 900px) {
  .detail {
    grid-template-columns: 1fr;
  }
}
</style>
