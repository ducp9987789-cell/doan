<template>
  <section class="section">
    <div class="container">
      <h1 class="section-title">My orders</h1>
      <p class="section-desc">Track order status after checkout.</p>

      <div v-if="!orders.length" class="panel">No orders yet.</div>
      <article v-for="order in orders" :key="order.id" class="panel order">
        <div class="top">
          <strong>#{{ order.id.slice(-6).toUpperCase() }}</strong>
          <span class="status">{{ order.status }}</span>
        </div>
        <p class="muted">{{ formatDate(order.created_at) }}</p>
        <ul>
          <li v-for="item in order.items" :key="`${item.product_id}-${item.size}`">
            {{ item.name }} × {{ item.quantity }}
          </li>
        </ul>
        <p>Total: <strong>{{ formatPrice(order.total) }}</strong></p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { orderApi } from '../services'

const orders = ref([])

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('vi-VN') : ''
}

onMounted(async () => {
  const { data } = await orderApi.myOrders()
  orders.value = data
})
</script>

<style scoped>
.order {
  margin-bottom: 1rem;
}

.top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.status {
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.85rem;
  color: var(--accent);
}
</style>
