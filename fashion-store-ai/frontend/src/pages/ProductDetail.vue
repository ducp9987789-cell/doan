<template>
  <section class="section product-detail-section" v-if="product">
    <div class="container">
      <!-- Breadcrumb -->
      <nav class="breadcrumb">
        <RouterLink to="/">Trang chủ</RouterLink>
        <span>/</span>
        <RouterLink :to="{ name: 'products', query: { category_id: product.category_id } }">
          {{ product.category_name || 'Thời trang' }}
        </RouterLink>
        <span>/</span>
        <span class="current">{{ product.name }}</span>
      </nav>

      <div class="detail-grid">
        <!-- Ảnh sản phẩm -->
        <div class="media-column fade-up">
          <div class="main-image-wrapper">
            <img :src="product.images?.[0] || placeholder" :alt="product.name" class="main-image" />
            <span v-if="discountPercent" class="badge-sale">-{{ discountPercent }}%</span>
          </div>
        </div>

        <!-- Thông tin sản phẩm -->
        <div class="info-column fade-up">
          <span class="category-badge">{{ product.category_name || 'Thời trang cao cấp' }}</span>
          <h1 class="product-title">{{ product.name }}</h1>

          <div class="price-box">
            <span class="sale-price">{{ formatPrice(product.sale_price || product.price) }}</span>
            <span v-if="product.sale_price && product.sale_price < product.price" class="old-price">
              {{ formatPrice(product.price) }}
            </span>
          </div>

          <p class="product-description">{{ product.description }}</p>

          <hr class="divider" />

          <!-- Tùy chọn Màu sắc -->
          <div class="option-group" v-if="product.colors?.length">
            <label class="option-label">Chọn màu sắc: <strong>{{ selectedColor }}</strong></label>
            <div class="option-pills">
              <button
                v-for="c in product.colors"
                :key="c"
                type="button"
                class="pill-btn"
                :class="{ active: selectedColor === c }"
                @click="selectedColor = c"
              >
                {{ c }}
              </button>
            </div>
          </div>

          <!-- Tùy chọn Kích thước -->
          <div class="option-group" v-if="product.sizes?.length">
            <div class="size-header">
              <label class="option-label">Chọn kích cỡ: <strong>{{ selectedSize }}</strong></label>
              <button class="btn-size-guide" type="button" @click="showSizeGuide = !showSizeGuide">
                📐 Bảng size chuẩn
              </button>
            </div>
            <div class="option-pills">
              <button
                v-for="s in product.sizes"
                :key="s"
                type="button"
                class="pill-btn"
                :class="{ active: selectedSize === s }"
                @click="selectedSize = s"
              >
                {{ s }}
              </button>
            </div>
          </div>

          <!-- Bảng size popup toggle -->
          <div v-if="showSizeGuide" class="size-guide-box panel">
            <strong>Bảng gợi ý kích thước (Theo chiều cao & cân nặng):</strong>
            <ul>
              <li><strong>Size S:</strong> 1m50 - 1m62, 45 - 53kg</li>
              <li><strong>Size M:</strong> 1m60 - 1m70, 54 - 62kg</li>
              <li><strong>Size L:</strong> 1m68 - 1m76, 63 - 72kg</li>
              <li><strong>Size XL:</strong> 1m75 - 1m85, 73 - 85kg</li>
            </ul>
          </div>

          <!-- Số lượng & Nút Thêm Giỏ Hàng -->
          <div class="action-row">
            <div class="quantity-picker">
              <button type="button" @click="quantity = Math.max(1, quantity - 1)">-</button>
              <input v-model.number="quantity" type="number" min="1" max="99" />
              <button type="button" @click="quantity = quantity + 1">+</button>
            </div>

            <button class="btn btn-add-cart" :disabled="adding" @click="addToCart">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <span>{{ adding ? 'Đang thêm vào giỏ...' : 'Thêm vào giỏ hàng' }}</span>
            </button>
          </div>

          <!-- Thông báo -->
          <div v-if="message" class="alert-box" :class="{ success: isSuccess }">
            {{ message }}
          </div>

          <!-- Cam kết dịch vụ -->
          <div class="guarantees panel">
            <div class="guarantee-item">
              <span class="g-icon">🚚</span>
              <div>
                <strong>Giao hàng toàn quốc</strong>
                <p>Nhận hàng trong 2-3 ngày, kiểm tra trước khi nhận</p>
              </div>
            </div>
            <div class="guarantee-item">
              <span class="g-icon">🔄</span>
              <div>
                <strong>Đổi trả 30 ngày miễn phí</strong>
                <p>Hỗ trợ đổi size hoặc đổi mẫu nhanh chóng</p>
              </div>
            </div>
            <div class="guarantee-item">
              <span class="g-icon">🛡️</span>
              <div>
                <strong>Cam kết 100% chính hãng</strong>
                <p>Đền tiền gấp 10 lần nếu phát hiện hàng giả</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section v-else class="section">
    <div class="container text-center">
      <p class="muted">Đang tải thông tin chi tiết sản phẩm...</p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../services'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()

const product = ref(null)
const selectedColor = ref('')
const selectedSize = ref('')
const quantity = ref(1)
const adding = ref(false)
const message = ref('')
const isSuccess = ref(false)
const showSizeGuide = ref(false)

const placeholder = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'

const discountPercent = computed(() => {
  if (product.value?.sale_price && product.value?.price && product.value.sale_price < product.value.price) {
    return Math.round(((product.value.price - product.value.sale_price) / product.value.price) * 100)
  }
  return null
})

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
      color: selectedColor.value,
      size: selectedSize.value,
    })
    isSuccess.value = true
    message.value = '✓ Đã thêm sản phẩm vào giỏ hàng thành công!'
    setTimeout(() => {
      message.value = ''
    }, 4000)
  } catch (error) {
    isSuccess.value = false
    message.value = error.response?.data?.detail || 'Không thể thêm vào giỏ hàng. Vui lòng thử lại.'
  } finally {
    adding.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await productApi.get(route.params.id)
    product.value = data
    selectedColor.value = data.colors?.[0] || ''
    selectedSize.value = data.sizes?.[0] || ''
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.88rem;
  color: var(--muted);
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.breadcrumb a {
  color: var(--ink);
  transition: color 0.2s ease;
}

.breadcrumb a:hover {
  color: var(--accent);
}

.breadcrumb .current {
  color: var(--accent);
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 3rem;
  align-items: start;
}

.main-image-wrapper {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--line);
  background: var(--bg-deep);
}

.main-image {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
}

.badge-sale {
  position: absolute;
  top: 18px;
  left: 18px;
  background: var(--danger);
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 800;
  padding: 6px 12px;
  border-radius: 999px;
  box-shadow: 0 4px 12px rgba(179, 57, 57, 0.4);
}

.category-badge {
  display: inline-block;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent-gold);
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.product-title {
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 4vw, 3.2rem);
  line-height: 1.15;
  margin: 0 0 1rem;
}

.price-box {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.sale-price {
  font-size: 2rem;
  font-weight: 800;
  color: var(--accent);
}

.old-price {
  font-size: 1.25rem;
  color: var(--muted);
  text-decoration: line-through;
}

.product-description {
  font-size: 1.02rem;
  line-height: 1.6;
  color: var(--ink-light);
  margin-bottom: 1.5rem;
}

.divider {
  border: none;
  border-top: 1px solid var(--line);
  margin: 1.5rem 0;
}

.option-group {
  margin-bottom: 1.4rem;
}

.option-label {
  display: block;
  font-size: 0.92rem;
  margin-bottom: 0.6rem;
  color: var(--ink);
}

.size-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}

.size-header .option-label {
  margin-bottom: 0;
}

.btn-size-guide {
  border: none;
  background: transparent;
  color: var(--accent);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.option-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill-btn {
  border: 1.5px solid var(--line-strong);
  background: #ffffff;
  padding: 0.55rem 1.1rem;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  border-color: var(--accent);
}

.pill-btn.active {
  border-color: var(--accent);
  background: var(--accent);
  color: #ffffff;
}

.size-guide-box {
  margin-bottom: 1.4rem;
  font-size: 0.88rem;
  background: #fffdf9;
}

.size-guide-box ul {
  margin: 0.5rem 0 0 1.2rem;
  padding: 0;
}

.action-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.quantity-picker {
  display: flex;
  align-items: center;
  border: 1.5px solid var(--line-strong);
  border-radius: 999px;
  background: #ffffff;
  overflow: hidden;
}

.quantity-picker button {
  width: 40px;
  height: 48px;
  border: none;
  background: transparent;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--ink);
  cursor: pointer;
  transition: background 0.2s ease;
}

.quantity-picker button:hover {
  background: var(--bg);
}

.quantity-picker input {
  width: 45px;
  border: none;
  text-align: center;
  font-weight: 700;
  font-size: 1rem;
  background: transparent;
  outline: none;
}

.btn-add-cart {
  flex: 1;
  font-size: 1.05rem;
  padding: 0.85rem 1.8rem;
}

.alert-box {
  padding: 0.85rem 1.2rem;
  border-radius: 12px;
  font-weight: 600;
  margin-bottom: 1.5rem;
  background: var(--danger-soft);
  color: var(--danger);
}

.alert-box.success {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.guarantees {
  display: grid;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.7);
  padding: 1.2rem;
}

.guarantee-item {
  display: flex;
  gap: 0.8rem;
  align-items: center;
}

.g-icon {
  font-size: 1.3rem;
}

.guarantee-item strong {
  display: block;
  font-size: 0.9rem;
  color: var(--ink);
}

.guarantee-item p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted);
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}
</style>
