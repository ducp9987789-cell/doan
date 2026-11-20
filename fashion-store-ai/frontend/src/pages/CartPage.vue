<template>
  <section class="section cart-page">
    <div class="container">
      <h1 class="section-title">Giỏ hàng của bạn</h1>
      <p class="section-desc">Kiểm tra lại danh sách các món đồ thời trang đã chọn trước khi thanh toán.</p>

      <!-- Giỏ hàng trống -->
      <div v-if="!cart.items.length" class="panel empty-cart">
        <div class="empty-cart-icon">🛒</div>
        <h2>Giỏ hàng của bạn đang trống</h2>
        <p class="muted">Chưa có sản phẩm nào được thêm vào giỏ hàng. Hãy khám phá ngay các bộ sưu tập mới nhất nhé!</p>
        <RouterLink class="btn" to="/products">Tiếp tục mua sắm</RouterLink>
      </div>

      <!-- Danh sách sản phẩm trong giỏ -->
      <div v-else class="cart-layout">
        <div class="panel cart-items-panel">
          <div class="cart-header">
            <span>Sản phẩm</span>
            <span>Số lượng & Giá</span>
          </div>

          <article
            v-for="item in cart.items"
            :key="`${item.product_id}-${item.color}-${item.size}`"
            class="cart-item-row"
          >
            <div class="item-media">
              <img :src="item.image || placeholder" :alt="item.name" />
            </div>

            <div class="item-info">
              <h3 class="item-name">
                <RouterLink :to="`/products/${item.product_id}`">{{ item.name }}</RouterLink>
              </h3>
              <div class="item-specs">
                <span v-if="item.color" class="spec-tag">Màu: {{ item.color }}</span>
                <span v-if="item.size" class="spec-tag">Size: {{ item.size }}</span>
                <span v-if="item.stock !== undefined && item.stock <= 0" class="stock-tag out-of-stock">Hết hàng</span>
                <span v-else-if="item.stock !== undefined && item.quantity > item.stock" class="stock-tag over-stock">Chỉ còn {{ item.stock }} món</span>
                <span v-else-if="item.stock !== undefined && item.stock <= 5" class="stock-tag low-stock">Còn {{ item.stock }} sản phẩm</span>
              </div>
              <p class="item-unit-price">{{ formatPrice(item.price) }}</p>
            </div>

            <div class="item-actions">
              <div class="qty-picker">
                <button type="button" @click="changeQty(item, item.quantity - 1)">-</button>
                <span>{{ item.quantity }}</span>
                <button
                  type="button"
                  :disabled="item.stock !== undefined && item.quantity >= item.stock"
                  :title="item.stock !== undefined && item.quantity >= item.stock ? 'Đã đạt giới hạn số lượng còn lại trong kho' : 'Tăng số lượng'"
                  @click="changeQty(item, item.quantity + 1)"
                >
                  +
                </button>
              </div>

              <div class="item-total-price">
                <strong>{{ formatPrice(item.price * item.quantity) }}</strong>
              </div>

              <button class="btn-remove" @click="changeQty(item, 0)" title="Xóa món này khỏi giỏ">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </article>
        </div>

        <!-- Cột tóm tắt thanh toán -->
        <aside class="panel cart-summary-panel">
          <h3 class="summary-title">Tóm tắt đơn hàng</h3>

          <div class="summary-row">
            <span>Tạm tính ({{ cart.itemCount }} món):</span>
            <strong>{{ formatPrice(cart.subtotal) }}</strong>
          </div>

          <div class="summary-row">
            <span>Phí vận chuyển:</span>
            <span v-if="cart.subtotal >= 500000" class="text-free">Miễn phí (Đơn > 500k)</span>
            <span v-else>{{ formatPrice(30000) }}</span>
          </div>

          <hr class="summary-divider" />

          <div class="summary-row total-row">
            <span>Tổng thanh toán:</span>
            <strong class="grand-total">
              {{ formatPrice(cart.subtotal + (cart.subtotal >= 500000 ? 0 : 30000)) }}
            </strong>
          </div>

          <!-- Cảnh báo lỗi tồn kho -->
          <div v-if="cartError" class="cart-error-alert">
            {{ cartError }}
          </div>

          <div v-if="hasInvalidStock" class="cart-stock-warning-alert">
            ⚠️ Một số món trong giỏ hàng hiện đã hết hoặc số lượng chọn vượt quá số lượng hàng có sẵn trong kho. Vui lòng điều chỉnh lại trước khi thanh toán.
          </div>

          <button
            v-if="hasInvalidStock"
            type="button"
            class="btn btn-checkout btn-block btn-disabled"
            disabled
            title="Vui lòng điều chỉnh số lượng sản phẩm hợp lệ"
          >
            <span>Tiến hành đặt hàng</span>
          </button>

          <RouterLink v-else class="btn btn-checkout btn-block" to="/checkout">
            <span>Tiến hành đặt hàng</span>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </RouterLink>

          <RouterLink class="btn secondary btn-continue btn-block" to="/products">
            ← Tiếp tục chọn thêm đồ
          </RouterLink>

          <div class="security-note">
            <span>🔒 Thanh toán an toàn & Bảo mật 100%</span>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useCartStore } from '../stores/cart'

const cart = useCartStore()
const cartError = ref('')
const placeholder = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'

const hasInvalidStock = computed(() => {
  return cart.items.some(it => it.stock !== undefined && (it.stock <= 0 || it.quantity > it.stock))
})

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

async function changeQty(item, quantity) {
  cartError.value = ''
  if (quantity > item.quantity && item.stock !== undefined && quantity > item.stock) {
    cartError.value = `Sản phẩm '${item.name}' chỉ còn ${item.stock} sản phẩm trong kho.`
    return
  }
  try {
    await cart.updateItem(item.product_id, quantity, item.color, item.size)
  } catch (err) {
    cartError.value = err.response?.data?.detail || 'Không thể cập nhật số lượng sản phẩm.'
  }
}

onMounted(() => cart.fetchCart())
</script>

<style scoped>
.empty-cart {
  text-align: center;
  padding: 4rem 2rem;
  background: #ffffff;
}

.empty-cart-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.empty-cart h2 {
  font-family: var(--font-display);
  font-size: 2rem;
  margin: 0 0 0.5rem;
}

.empty-cart p {
  margin: 0 0 2rem;
}

.cart-layout {
  display: grid;
  grid-template-columns: 1.4fr 0.6fr;
  gap: 2rem;
  align-items: start;
}

.cart-items-panel {
  background: #ffffff;
  padding: 1.8rem;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--muted);
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1rem;
}

.cart-item-row {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 1.2rem;
  padding: 1.2rem 0;
  border-bottom: 1px solid var(--line);
  align-items: center;
}

.item-media img {
  width: 100px;
  height: 120px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  background: var(--bg-deep);
}

.item-name {
  margin: 0 0 0.4rem;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.4;
}

.item-name a {
  color: var(--ink);
  transition: color 0.2s ease;
}

.item-name a:hover {
  color: var(--accent);
}

.item-specs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.spec-tag {
  font-size: 0.78rem;
  background: var(--bg);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--muted);
}

.stock-tag {
  font-size: 0.75rem;
  padding: 2px 7px;
  border-radius: 4px;
  font-weight: 600;
}

.stock-tag.out-of-stock {
  background: #fee2e2;
  color: #b91c1c;
}

.stock-tag.over-stock {
  background: #ffedd5;
  color: #c2410c;
}

.stock-tag.low-stock {
  background: #fef9c3;
  color: #854d0e;
}

.qty-picker button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.cart-error-alert {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
}

.cart-stock-warning-alert {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 8px;
  font-size: 0.82rem;
  line-height: 1.4;
}

.btn-disabled {
  background: #e2e8f0 !important;
  color: #94a3b8 !important;
  cursor: not-allowed !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: none !important;
}

.item-unit-price {
  margin: 0;
  color: var(--accent);
  font-weight: 700;
  font-size: 0.95rem;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.qty-picker {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  background: #ffffff;
}

.qty-picker button {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 700;
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
}

.qty-picker button:hover {
  background: var(--bg);
}

.qty-picker span {
  width: 32px;
  text-align: center;
  font-weight: 700;
  font-size: 0.92rem;
}

.item-total-price {
  min-width: 100px;
  text-align: right;
  font-size: 1.05rem;
  color: var(--ink);
}

.btn-remove {
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-remove:hover {
  color: var(--danger);
  background: var(--danger-soft);
}

/* Summary Panel */
.cart-summary-panel {
  background: #ffffff;
  padding: 1.8rem;
}

.summary-title {
  margin: 0 0 1.2rem;
  font-family: var(--font-display);
  font-size: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.9rem;
  font-size: 0.95rem;
  color: var(--ink-light);
}

.text-free {
  color: #2e7d32;
  font-weight: 700;
}

.summary-divider {
  border: none;
  border-top: 1px solid var(--line);
  margin: 1.2rem 0;
}

.total-row {
  font-size: 1.1rem;
  color: var(--ink);
}

.grand-total {
  font-size: 1.4rem;
  color: var(--accent);
  font-weight: 800;
}

.btn-block {
  width: 100%;
}

.btn-checkout {
  padding: 0.95rem;
  font-size: 1.05rem;
  margin-top: 1.2rem;
}

.btn-continue {
  margin-top: 0.8rem;
  padding: 0.75rem;
  font-size: 0.9rem;
}

.security-note {
  margin-top: 1.2rem;
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
}

@media (max-width: 992px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .cart-item-row {
    grid-template-columns: 75px 1fr;
    gap: 0.8rem;
  }
  .item-actions {
    grid-column: 1 / -1;
    justify-content: space-between;
    padding-top: 0.6rem;
  }
}
</style>
