<template>
  <section class="section orders-page">
    <div class="container">
      <!-- Thông báo đặt hàng thành công -->
      <div v-if="showSuccessBanner" class="panel order-success-banner">
        <div class="success-icon">🎉</div>
        <div class="success-body">
          <h3>Đặt hàng thành công!</h3>
          <p>Cảm ơn bạn đã mua sắm tại <strong>Fashion Store</strong>. Đơn hàng mới nhất của bạn đã được tiếp nhận và hiển thị ngay bên dưới.</p>
        </div>
      </div>

      <div class="orders-head">
        <div>
          <h1 class="section-title">Đơn hàng của tôi</h1>
          <p class="section-desc">Theo dõi tiến độ giao hàng và xem lại lịch sử các đơn hàng bạn đã đặt.</p>
        </div>
        <button class="btn-refresh" @click="fetchOrders" :disabled="loading" title="Cập nhật danh sách đơn hàng">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M23 4v6h-6M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          <span>{{ loading ? 'Đang tải...' : 'Làm mới' }}</span>
        </button>
      </div>

      <div v-if="loading && !orders.length" class="panel text-center">
        <p>Đang tải danh sách đơn hàng...</p>
      </div>

      <div v-else-if="!orders.length" class="panel empty-orders text-center">
        <div class="empty-icon">📦</div>
        <h3>Bạn chưa có đơn hàng nào</h3>
        <p class="muted">Hãy đặt hàng ngay hôm nay để trải nghiệm dịch vụ thời trang thông minh từ Fashion Store!</p>
        <RouterLink class="btn" to="/products">Khám phá sản phẩm</RouterLink>
      </div>

      <div v-else class="orders-list">
        <article v-for="order in orders" :key="order.id" class="panel order-card">
          <div class="order-top">
            <div class="order-meta">
              <span class="order-code">Mã đơn: #{{ order.id.slice(-6).toUpperCase() }}</span>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <span class="order-status-badge" :class="order.status">
              {{ formatStatus(order.status) }}
            </span>
          </div>

          <div class="order-items-list">
            <div
              v-for="item in order.items"
              :key="`${item.product_id}-${item.size}-${item.color}`"
              class="order-item-row"
            >
              <div class="order-item-name">
                <strong>{{ item.name }}</strong>
                <span class="order-item-spec" v-if="item.color || item.size">
                  ({{ [item.color, item.size].filter(Boolean).join(' / ') }})
                </span>
              </div>
              <div class="order-item-qty">
                x {{ item.quantity }}
              </div>
              <div class="order-item-price">
                {{ formatPrice(item.price * item.quantity) }}
              </div>
            </div>
          </div>

          <div class="order-bottom">
            <div class="shipping-info" v-if="order.shipping_address">
              <small class="muted">
                Giao đến: {{ order.shipping_address.full_name }} · {{ order.shipping_address.phone }} · {{ order.shipping_address.address }}, {{ order.shipping_address.city }}
              </small>
            </div>
            <div class="order-total">
              <span>Tổng thanh toán:</span>
              <strong class="total-amount">{{ formatPrice(order.total) }}</strong>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { orderApi } from '../services'

const route = useRoute()
const orders = ref([])
const loading = ref(false)
const showSuccessBanner = ref(false)

const statusMap = {
  pending: 'Chờ xác nhận',
  confirmed: 'Đã duyệt đơn',
  shipping: 'Đang giao hàng',
  completed: 'Giao thành công',
  cancelled: 'Đã hủy đơn',
}

function formatStatus(status) {
  return statusMap[status] || status
}

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('vi-VN') : ''
}

async function fetchOrders() {
  loading.value = true
  try {
    const { data } = await orderApi.myOrders()
    orders.value = data || []
  } catch (error) {
    console.error('Lỗi khi tải đơn hàng:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.success) {
    showSuccessBanner.value = true
  }
  fetchOrders()
})

watch(
  () => route.fullPath,
  () => {
    if (route.query.success) {
      showSuccessBanner.value = true
    }
    fetchOrders()
  }
)
</script>

<style scoped>
.order-success-banner {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 2rem;
}

.success-icon {
  font-size: 2.2rem;
}

.success-body h3 {
  margin: 0 0 0.3rem;
  font-size: 1.15rem;
  color: #166534;
}

.success-body p {
  margin: 0;
  color: #15803d;
  font-size: 0.92rem;
}

.orders-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #d1d5db;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-orders {
  padding: 4rem 2rem;
  background: #ffffff;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
}

.empty-orders h3 {
  font-size: 1.3rem;
  margin: 0 0 0.5rem;
}

.empty-orders p {
  margin: 0 0 1.5rem;
}

.orders-list {
  display: grid;
  gap: 1.5rem;
}

.order-card {
  background: #ffffff;
  padding: 1.6rem;
}

.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.order-code {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--ink);
}

.order-date {
  font-size: 0.85rem;
  color: var(--muted);
}

.order-status-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.order-status-badge.pending {
  background: #fff8e1;
  color: #b78103;
}

.order-status-badge.confirmed {
  background: #e1f5fe;
  color: #0277bd;
}

.order-status-badge.shipping {
  background: #e8f5e9;
  color: #2e7d32;
}

.order-status-badge.completed {
  background: var(--accent-light);
  color: var(--accent);
}

.order-status-badge.cancelled {
  background: var(--danger-soft);
  color: var(--danger);
}

.order-items-list {
  padding: 1rem 0;
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 0.8rem;
}

.order-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
}

.order-item-name strong {
  color: var(--ink);
}

.order-item-spec {
  color: var(--muted);
  font-size: 0.85rem;
  margin-left: 0.4rem;
}

.order-item-qty {
  color: var(--muted);
}

.order-item-price {
  font-weight: 600;
  color: var(--ink);
}

.order-bottom {
  padding-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.shipping-info {
  flex: 1;
}

.order-total {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}

.total-amount {
  font-size: 1.25rem;
  color: var(--accent);
  font-weight: 800;
}
</style>
