<template>
  <header class="header">
    <div class="container header-inner">
      <RouterLink to="/" class="logo">LUMIA</RouterLink>
      <nav>
        <RouterLink to="/products">Products</RouterLink>
        <RouterLink to="/orders" v-if="auth.isAuthenticated">Orders</RouterLink>
        <RouterLink to="/admin" v-if="auth.isAdmin">Admin</RouterLink>
      </nav>
      <div class="actions">
        <RouterLink to="/cart" class="cart-link">Cart ({{ cart.itemCount }})</RouterLink>
        <RouterLink v-if="!auth.isAuthenticated" to="/login" class="btn secondary">Sign in</RouterLink>
        <button v-else class="btn secondary" @click="logout">Sign out</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()

async function loadCart() {
  if (auth.isAuthenticated) {
    try {
      await cart.fetchCart()
    } catch {
      cart.reset()
    }
  } else {
    cart.reset()
  }
}

function logout() {
  auth.logout()
  cart.reset()
  router.push('/')
}

onMounted(loadCart)
watch(() => auth.isAuthenticated, loadCart)
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(14px);
  background: rgba(247, 242, 234, 0.78);
  border-bottom: 1px solid var(--line);
}

.header-inner {
  min-height: 74px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.logo {
  font-family: var(--font-display);
  font-size: 2rem;
  letter-spacing: 0.08em;
}

nav {
  display: flex;
  gap: 1.25rem;
}

nav a {
  color: var(--muted);
}

nav a.router-link-active {
  color: var(--ink);
  font-weight: 600;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.cart-link {
  font-weight: 600;
}

@media (max-width: 768px) {
  .header-inner {
    flex-wrap: wrap;
    padding: 0.8rem 0;
  }

  nav {
    order: 3;
    width: 100%;
  }
}
</style>
