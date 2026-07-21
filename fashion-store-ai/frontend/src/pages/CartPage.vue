<template>
  <section class="section">
    <div class="container">
      <h1 class="section-title">Cart</h1>
      <p class="section-desc">Review selected items before checkout.</p>

      <div v-if="!cart.items.length" class="panel">
        <p>Your cart is empty.</p>
        <RouterLink class="btn" to="/products">Continue shopping</RouterLink>
      </div>

      <div v-else class="layout">
        <div class="panel items">
          <article v-for="item in cart.items" :key="`${item.product_id}-${item.color}-${item.size}`" class="row">
            <img :src="item.image" :alt="item.name" />
            <div>
              <h3>{{ item.name }}</h3>
              <p class="muted">{{ item.color }} / {{ item.size }}</p>
              <p>{{ formatPrice(item.price) }}</p>
              <div class="qty">
                <button @click="changeQty(item, item.quantity - 1)">-</button>
                <span>{{ item.quantity }}</span>
                <button @click="changeQty(item, item.quantity + 1)">+</button>
              </div>
            </div>
          </article>
        </div>
        <aside class="panel summary">
          <h3>Summary</h3>
          <p>Subtotal: <strong>{{ formatPrice(cart.subtotal) }}</strong></p>
          <RouterLink class="btn" to="/checkout">Checkout</RouterLink>
        </aside>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '../stores/cart'

const cart = useCartStore()

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

async function changeQty(item, quantity) {
  await cart.updateItem(item.product_id, quantity, item.color, item.size)
}

onMounted(() => cart.fetchCart())
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 1.4fr 0.6fr;
  gap: 1.2rem;
}

.row {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 1rem;
  padding: 0.9rem 0;
  border-bottom: 1px solid var(--line);
}

.row img {
  width: 110px;
  height: 130px;
  object-fit: cover;
}

.row h3 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.5rem;
}

.qty {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.qty button {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: white;
  cursor: pointer;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
