<template>
  <RouterLink :to="`/products/${product.id}`" class="product-card" :title="product.name">
    <div class="img-wrapper">
      <img :src="product.images?.[0] || placeholder" :alt="product.name" loading="lazy" />
      
      <!-- Giảm giá % badge -->
      <span v-if="discountPercent" class="badge-sale">-{{ discountPercent }}%</span>
      
      <!-- Nổi bật badge -->
      <span v-else-if="product.is_featured" class="badge-featured">Hot</span>
    </div>

    <div class="card-body">
      <span class="category-name">{{ product.category_name || 'Thời trang' }}</span>
      <h3 class="product-title">{{ product.name }}</h3>
      
      <div class="price-row">
        <span class="sale-price">{{ formatPrice(product.sale_price || product.price) }}</span>
        <span v-if="product.sale_price && product.sale_price < product.price" class="old-price">
          {{ formatPrice(product.price) }}
        </span>
      </div>

      <div class="card-actions">
        <button
          type="button"
          class="btn-add-cart"
          :class="{ 'btn-added': addedRecently }"
          :disabled="isAdding"
          @click.stop.prevent="handleAddToCart"
        >
          <svg v-if="!addedRecently" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="9" cy="21" r="1"></circle>
            <circle cx="20" cy="21" r="1"></circle>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span>{{ addedRecently ? 'Đã thêm!' : isAdding ? 'Đang thêm...' : 'Thêm vào giỏ' }}</span>
        </button>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const props = defineProps({
  product: { type: Object, required: true },
})

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()

const isAdding = ref(false)
const addedRecently = ref(false)

const placeholder = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'

const discountPercent = computed(() => {
  if (props.product.sale_price && props.product.price && props.product.sale_price < props.product.price) {
    return Math.round(((props.product.price - props.product.sale_price) / props.product.price) * 100)
  }
  return null
})

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

async function handleAddToCart() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  isAdding.value = true
  try {
    await cart.addItem({
      product_id: props.product.id,
      quantity: 1,
      color: props.product.colors?.[0] || 'Mặc định',
      size: props.product.sizes?.[0] || 'M',
    })
    addedRecently.value = true
    setTimeout(() => {
      addedRecently.value = false
    }, 1800)
  } catch (error) {
    console.error('Lỗi thêm giỏ hàng:', error)
  } finally {
    isAdding.value = false
  }
}
</script>

<style scoped>
.product-card {
  position: relative;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.img-wrapper {
  position: relative;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  background: #f3f4f6;
}

.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .img-wrapper img {
  transform: scale(1.03);
}

.badge-sale {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #dc2626;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 7px;
  border-radius: 4px;
  z-index: 2;
}

.badge-featured {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #0f766e;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: 4px;
  z-index: 2;
}

.card-body {
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 0.4rem;
}

.category-name {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.product-title {
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.35;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6em;
}

.price-row {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 0.2rem;
}

.sale-price {
  color: #dc2626;
  font-weight: 700;
  font-size: 1.05rem;
}

.old-price {
  color: #9ca3af;
  text-decoration: line-through;
  font-size: 0.82rem;
}

.card-actions {
  margin-top: 0.6rem;
}

.btn-add-cart {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background: #f8fafc;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  padding: 0.55rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-cart:hover:not(:disabled) {
  background: #114b43;
  color: #ffffff;
  border-color: #114b43;
}

.btn-add-cart:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-add-cart.btn-added {
  background: #16a34a;
  color: #ffffff;
  border-color: #16a34a;
}

.btn-add-cart:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
