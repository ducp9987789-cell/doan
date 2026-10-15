<template>
  <header class="header">
    <!-- Hàng trên: Logo, Ô tìm kiếm với kính lúp, Giỏ hàng, Đăng nhập/Đăng ký -->
    <div class="header-main">
      <div class="container header-main-inner">
        <!-- Bên trái: Tên cửa hàng Fashion Store -->
        <RouterLink to="/" class="brand-logo" title="Fashion Store AI - Trang chủ">
          <div class="brand-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </div>
          <div class="brand-text">
            <span class="brand-name">FASHION STORE</span>
            <span class="brand-sub">AI Shopping Boutique</span>
          </div>
        </RouterLink>

        <!-- Ở giữa: Ô tìm kiếm có icon kính lúp -->
        <div class="search-box">
          <form @submit.prevent="handleSearch" class="search-form">
            <div class="search-input-wrapper">
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="Tìm kiếm áo sơ mi, quần jean, váy đầm, túi xách..."
                aria-label="Tìm kiếm sản phẩm"
              />
              <button type="submit" class="search-btn" title="Tìm kiếm">
                <!-- Icon kính lúp -->
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </button>
            </div>
          </form>
        </div>

        <!-- Bên phải: Icon xe đẩy giỏ hàng, Đăng nhập, Đăng ký -->
        <div class="header-actions">
          <!-- Icon xe đẩy giỏ hàng (Ẩn trên homepage theo yêu cầu, khi đăng nhập xong ẩn text chỉ giữ icon) -->
          <RouterLink
            v-if="route.name !== 'home' && !auth.isAdmin"
            to="/cart"
            class="cart-btn"
            title="Xem giỏ hàng của bạn"
          >
            <div class="cart-icon-wrapper">
              <!-- SVG icon xe đẩy siêu thị / shopping cart -->
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <span v-if="cart.itemCount > 0" class="cart-badge">{{ cart.itemCount > 99 ? '99+' : cart.itemCount }}</span>
            </div>
            <span v-if="!auth.isAuthenticated" class="cart-label">Giỏ hàng</span>
          </RouterLink>

          <!-- Nút tài khoản: Đăng nhập / Đăng ký hoặc Dropdown khi đã đăng nhập -->
          <div v-if="!auth.isAuthenticated" class="auth-buttons">
            <RouterLink to="/login" class="btn-auth-signin">Đăng nhập</RouterLink>
            <RouterLink to="/login?tab=register" class="btn-auth-signup">Đăng ký</RouterLink>
          </div>

          <div v-else class="user-menu">
            <RouterLink to="/orders" class="user-action-link" title="Đơn hàng của tôi">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
                <path d="M3 6h18" />
                <path d="M16 10a4 4 0 0 1-8 0" />
              </svg>
              <span>Đơn hàng của tôi</span>
            </RouterLink>

            <RouterLink v-if="auth.isAdmin" to="/admin" class="user-action-link admin-badge" title="Trang quản trị">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="7" height="9" x="3" y="3" rx="1" />
                <rect width="7" height="5" x="14" y="3" rx="1" />
                <rect width="7" height="9" x="14" y="12" rx="1" />
                <rect width="7" height="5" x="3" y="16" rx="1" />
              </svg>
              <span>Quản trị</span>
            </RouterLink>

            <button class="btn-logout" @click="handleLogout" title="Đăng xuất khỏi tài khoản">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              <span>Đăng xuất</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Dòng dưới: Danh mục sản phẩm (Tất cả sản phẩm, Áo, Quần, Váy, Giày, Túi...) -->
    <nav class="header-categories">
      <div class="container categories-inner">
        <RouterLink
          to="/products"
          class="cat-link"
          :class="{ active: isAllActive }"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <span>Tất cả sản phẩm</span>
        </RouterLink>

        <RouterLink
          v-for="cat in categoryList"
          :key="cat.id || cat.slug"
          :to="{ name: 'products', query: { category_id: cat.id } }"
          class="cat-link"
          :class="{ active: currentCategoryId === cat.id }"
        >
          <span>{{ cat.name }}</span>
        </RouterLink>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../services'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref(route.query.q || '')
const categoryList = ref([])

const defaultCategories = [
  { id: '', name: 'Áo Nam & Nữ', slug: 'ao' },
  { id: '', name: 'Quần Thời Trang', slug: 'quan' },
  { id: '', name: 'Váy & Đầm Nữ', slug: 'vay' },
  { id: '', name: 'Áo Khoác & Blazer', slug: 'ao-khoac' },
  { id: '', name: 'Giày & Dép', slug: 'giay-dep' },
  { id: '', name: 'Phụ Kiện Cao Cấp', slug: 'phu-kien' },
]

const currentCategoryId = computed(() => route.query.category_id || '')
const isAllActive = computed(() => route.name === 'products' && !route.query.category_id && !route.query.q)

async function loadCategories() {
  try {
    const { data } = await productApi.categories()
    if (data && data.length > 0) {
      categoryList.value = data
    } else {
      categoryList.value = defaultCategories
    }
  } catch {
    categoryList.value = defaultCategories
  }
}

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

function handleSearch() {
  const query = searchQuery.value.trim()
  if (query) {
    router.push({ name: 'products', query: { q: query } })
  } else {
    router.push({ name: 'products' })
  }
}

function handleLogout() {
  auth.logout()
  cart.reset()
  router.push('/')
}

watch(
  () => route.query.q,
  (newQ) => {
    searchQuery.value = newQ || ''
  }
)

onMounted(() => {
  loadCategories()
  loadCart()
})

watch(() => auth.isAuthenticated, loadCart)
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 253, 249, 0.96);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--line);
  box-shadow: 0 4px 24px rgba(25, 23, 20, 0.06);
  transition: all 0.3s ease;
}

/* Hàng trên */
.header-main {
  border-bottom: 1px solid rgba(25, 23, 20, 0.06);
  padding: 0.75rem 0;
}

.header-main-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

/* Logo */
.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--accent);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(17, 75, 67, 0.25);
  transition: transform 0.25s ease;
}

.brand-logo:hover .brand-icon {
  transform: rotate(-6deg) scale(1.05);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--ink);
  line-height: 1.1;
}

.brand-sub {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent-gold);
  font-weight: 700;
}

/* Ô tìm kiếm ở giữa */
.search-box {
  flex: 1;
  max-width: 520px;
}

.search-form {
  width: 100%;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1.5px solid var(--line-strong);
  border-radius: 999px;
  padding: 2px 4px 2px 1.2rem;
  transition: all 0.25s ease;
  box-shadow: var(--shadow-sm);
}

.search-input-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(17, 75, 67, 0.15);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.65rem 0.5rem;
  font-size: 0.92rem;
  color: var(--ink);
  outline: none;
}

.search-input::placeholder {
  color: #9e9589;
  font-size: 0.88rem;
}

.search-btn {
  background: var(--accent);
  color: #ffffff;
  border: none;
  border-radius: 999px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: var(--accent-hover);
  transform: scale(1.05);
}

/* Phía bên phải: Giỏ hàng + Auth */
.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

/* Nút Giỏ hàng */
.cart-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--line);
  color: var(--ink);
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.25s ease;
}

.cart-btn:hover {
  background: #ffffff;
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.cart-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  color: var(--accent);
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -10px;
  background: var(--danger);
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 800;
  min-width: 19px;
  height: 19px;
  padding: 0 4px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(179, 57, 57, 0.4);
}

.cart-label {
  display: inline;
}

/* Auth Buttons */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-auth-signin {
  padding: 0.55rem 1rem;
  border-radius: 999px;
  color: var(--ink);
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid var(--line);
  background: transparent;
  transition: all 0.2s ease;
}

.btn-auth-signin:hover {
  border-color: var(--ink);
  background: rgba(255, 255, 255, 0.8);
}

.btn-auth-signup {
  padding: 0.55rem 1.15rem;
  border-radius: 999px;
  background: var(--accent);
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 3px 10px rgba(17, 75, 67, 0.2);
  transition: all 0.2s ease;
}

.btn-auth-signup:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

/* User Menu khi đã đăng nhập */
.user-menu {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.user-action-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--ink);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--line);
  transition: all 0.2s ease;
}

.user-action-link:hover {
  background: #ffffff;
  color: var(--accent);
}

.user-action-link.admin-badge {
  background: #fff8e1;
  border-color: #ffe082;
  color: #b78103;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--danger);
  background: transparent;
  border: 1px solid rgba(179, 57, 57, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background: var(--danger-soft);
  border-color: var(--danger);
}

/* Hàng dưới: Danh mục sản phẩm */
.header-categories {
  background: rgba(255, 255, 255, 0.7);
  border-top: 1px solid rgba(25, 23, 20, 0.04);
}

.categories-inner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  padding: 0.45rem 0;
}

.categories-inner::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.cat-link {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.95rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--muted);
  white-space: nowrap;
  transition: all 0.2s ease;
}

.cat-link:hover {
  color: var(--ink);
  background: rgba(17, 75, 67, 0.08);
}

.cat-link.active {
  background: var(--accent);
  color: #ffffff;
}

/* Responsive */
@media (max-width: 992px) {
  .header-main-inner {
    flex-wrap: wrap;
  }
  .search-box {
    order: 3;
    max-width: 100%;
    width: 100%;
  }
}

@media (max-width: 600px) {
  .cart-label {
    display: none;
  }
  .brand-sub {
    display: none;
  }
  .btn-auth-signin, .btn-auth-signup {
    padding: 0.45rem 0.8rem;
    font-size: 0.82rem;
  }
}
</style>
