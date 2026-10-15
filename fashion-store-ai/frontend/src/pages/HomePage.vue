<template>
  <div class="home-page">
    <!-- Hero Banner Thời Trang -->
    <section class="hero">
      <div class="container hero-grid fade-up">
        <!-- Cột bên trái: Giới thiệu & CTA -->
        <div class="hero-left">
          <h1 class="hero-title">FASHION STORE</h1>
          <p class="hero-lead">
            Nâng tầm phong cách cá nhân với tủ đồ chọn lọc thời thượng, kết hợp cùng <strong>Trợ lý AI Stylist</strong> tư vấn trang phục & chọn size chuẩn xác 24/7.
          </p>
          <div class="hero-cta-row">
            <RouterLink class="btn btn-hero-primary" to="/products">
              <span>Khám phá bộ sưu tập</span>
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </RouterLink>
            <button class="btn btn-hero-ghost" @click="scrollToSection('promos')">
              <span>Xem mã giảm giá HOT</span>
              <span class="badge-hot">Ưu đãi</span>
            </button>
          </div>

          <div class="hero-stats">
            <div class="stat-item">
              <strong>Mã giảm giá</strong>
              <span>Áp dụng tức thì</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <strong>30 Ngày</strong>
              <span>Đổi trả miễn phí</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <strong>24/7</strong>
              <span>AI Stylist tư vấn</span>
            </div>
          </div>
        </div>

        <!-- Cột bên phải: Card lớn Sản phẩm nổi bật tự chạy quảng cáo -->
        <div
          class="hero-right"
          v-if="carouselItems.length > 0"
          @mouseenter="pauseCarousel"
          @mouseleave="startCarousel"
        >
          <div class="hero-banner-card-wrapper">
            <RouterLink
              :to="`/products/${activeProduct.id}`"
              class="hero-banner-card"
              :key="activeProduct.id"
            >
              <div class="banner-img-box">
                <img
                  :src="activeProduct.images?.[0] || 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'"
                  :alt="activeProduct.name"
                  class="banner-img"
                />
                <div class="banner-badge-row">
                  <span class="banner-tag">🔥 SẢN PHẨM NỔI BẬT</span>
                  <span v-if="activeDiscount" class="banner-sale-tag">-{{ activeDiscount }}%</span>
                </div>
              </div>

              <div class="banner-info-overlay">
                <div class="banner-cat">{{ activeProduct.category_name || 'Thời trang cao cấp' }}</div>
                <h3 class="banner-title">{{ activeProduct.name }}</h3>
                <div class="banner-price-row">
                  <div class="banner-prices">
                    <span class="banner-sale-price">{{ formatPrice(activeProduct.sale_price || activeProduct.price) }}</span>
                    <span v-if="activeProduct.sale_price && activeProduct.sale_price < activeProduct.price" class="banner-old-price">
                      {{ formatPrice(activeProduct.price) }}
                    </span>
                  </div>
                  <span class="banner-btn-view">
                    <span>Xem chi tiết</span>
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                  </span>
                </div>
              </div>
            </RouterLink>

            <!-- Điều hướng Banner Carousel -->
            <button class="banner-nav prev" @click="prevSlide" aria-label="Sản phẩm trước">‹</button>
            <button class="banner-nav next" @click="nextSlide" aria-label="Sản phẩm tiếp theo">›</button>

            <!-- Chấm chỉ số trang (Dots) -->
            <div class="banner-dots">
              <button
                v-for="(_, idx) in carouselItems"
                :key="idx"
                class="dot-btn"
                :class="{ active: currentSlide === idx }"
                @click="currentSlide = idx"
                :aria-label="`Slide ${idx + 1}`"
              ></button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Khám phá theo danh mục -->
    <section class="section categories-section">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">Danh mục thời trang</h2>
            <p class="section-desc">Khám phá các phong cách đa dạng từ công sở thanh lịch đến dạo phố trẻ trung.</p>
          </div>
          <RouterLink to="/products" class="view-all-link">
            <span>Xem tất cả danh mục</span>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path>
            </svg>
          </RouterLink>
        </div>

        <div class="category-grid">
          <RouterLink
            v-for="cat in categories"
            :key="cat.id"
            class="category-card"
            :to="{ name: 'products', query: { category_id: cat.id } }"
          >
            <div class="category-card-content">
              <span class="category-tag">Thời trang</span>
              <h3 class="category-name">{{ cat.name }}</h3>
              <p class="category-desc">{{ cat.description }}</p>
              <span class="category-cta">
                <span>Khám phá</span>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </div>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- PHẦN GIỮA: CÁC SẢN PHẨM NỔI BẬT & BÁN CHẠY -->
    <section class="section products-section" id="products">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">Sản phẩm thời trang nổi bật</h2>
            <p class="section-desc">Tuyển tập những thiết kế bán chạy và được yêu thích nhất trong tuần.</p>
          </div>

          <!-- Tabs lọc nhanh trên trang chủ -->
          <div class="product-tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'all' }"
              @click="filterProducts('all')"
            >
              Tất cả
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'featured' }"
              @click="filterProducts('featured')"
            >
              Nổi bật 🔥
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'sale' }"
              @click="filterProducts('sale')"
            >
              Giảm giá %
            </button>
          </div>
        </div>

        <!-- Lưới hiển thị sản phẩm -->
        <div v-if="filteredProducts.length > 0" class="grid-products">
          <ProductCard v-for="item in filteredProducts" :key="item.id" :product="item" />
        </div>

        <div v-else class="empty-state panel">
          <p>Hiện chưa có sản phẩm nào trong mục này.</p>
          <RouterLink to="/products" class="btn">Xem toàn bộ cửa hàng</RouterLink>
        </div>

        <div class="products-more-row">
          <RouterLink to="/products" class="btn secondary btn-lg">
            <span>Xem thêm tất cả sản phẩm</span>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Khối Giới thiệu AI Stylist -->
    <section class="section ai-showcase-section">
      <div class="container">
        <div class="ai-banner">
          <div class="ai-banner-content">
            <span class="ai-badge">🤖 Công Nghệ Mua Sắm Thông Minh</span>
            <h2>Trợ lý ảo AI Stylist — Tư vấn outfit hoàn hảo cho bạn</h2>
            <p>
              Bạn chưa biết phối áo sơ mi với quần gì? Cần tìm đầm dự tiệc theo chiều cao và cân nặng? Hãy hỏi ngay AI Stylist ở góc phải màn hình để nhận gợi ý phối đồ chuẩn xác và phù hợp nhất!
            </p>
            <ul class="ai-features">
              <li>✔️ Gợi ý trang phục theo sự kiện (đi làm, đi chơi, dạ tiệc)</li>
              <li>✔️ Tư vấn chọn size chuẩn xác theo số đo cá nhân</li>
              <li>✔️ Tìm kiếm sản phẩm theo mức giá và sở thích màu sắc</li>
            </ul>
          </div>
          <div class="ai-banner-visual">
            <div class="ai-chat-mockup">
              <div class="mockup-header">
                <div class="mockup-avatar">AI</div>
                <div>
                  <strong>Lumia AI Stylist</strong>
                  <small>Đang trực tuyến</small>
                </div>
              </div>
              <div class="mockup-body">
                <div class="mockup-msg user">
                  Gợi ý cho mình một set đồ đi làm công sở thanh lịch dưới 700k nhé!
                </div>
                <div class="mockup-msg assistant">
                  Chào bạn! Mình gợi ý bạn kết hợp <strong>Áo sơ mi trắng Oxford Premium</strong> (329k) cùng <strong>Quần Tây Âu Ống Suông</strong> (420k). Tổng set chỉ 749k và bạn có thể áp mã <strong>WELCOME10</strong> để giảm thêm 10% nhé! ✨
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Khối Chương trình Khuyến Mãi & Voucher HOT -->
    <section id="promos" class="section promos-section">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">Mã giảm giá & Khuyến mãi HOT</h2>
            <p class="section-desc">Nhập mã ưu đãi khi thanh toán để được giảm giá trực tiếp trên đơn hàng.</p>
          </div>
        </div>

        <div class="promo-grid">
          <article v-for="promo in promotions" :key="promo.id" class="promo-card">
            <div class="promo-left">
              <div class="promo-discount-badge">
                <span class="discount-num">
                  {{ promo.discount_type === 'percent' ? `${promo.discount_value}%` : `${(promo.discount_value / 1000).toFixed(0)}k` }}
                </span>
                <span class="discount-label">GIẢM</span>
              </div>
            </div>
            <div class="promo-center">
              <h3>{{ promo.title }}</h3>
              <p class="promo-desc">{{ promo.description }}</p>
              <div class="promo-code-box">
                <span class="code-text">{{ promo.code }}</span>
                <button class="btn-copy" @click="copyCode(promo.code)" title="Sao chép mã">
                  {{ copiedCode === promo.code ? 'Đã chép! ✓' : 'Sao chép' }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import { productApi } from '../services'

const allProducts = ref([])
const categories = ref([])
const promotions = ref([])
const activeTab = ref('all')
const copiedCode = ref('')
const currentSlide = ref(0)
let carouselTimer = null

const carouselItems = computed(() => {
  const featured = allProducts.value.filter((p) => p.is_featured)
  if (featured.length > 0) return featured.slice(0, 6)
  return allProducts.value.slice(0, 6)
})

const activeProduct = computed(() => {
  if (carouselItems.value.length === 0) return null
  return carouselItems.value[currentSlide.value % carouselItems.value.length]
})

const activeDiscount = computed(() => {
  if (!activeProduct.value) return null
  const p = activeProduct.value
  if (p.sale_price && p.price && p.sale_price < p.price) {
    return Math.round(((p.price - p.sale_price) / p.price) * 100)
  }
  return null
})

function nextSlide() {
  if (carouselItems.value.length === 0) return
  currentSlide.value = (currentSlide.value + 1) % carouselItems.value.length
}

function prevSlide() {
  if (carouselItems.value.length === 0) return
  currentSlide.value = (currentSlide.value - 1 + carouselItems.value.length) % carouselItems.value.length
}

function startCarousel() {
  stopCarousel()
  carouselTimer = setInterval(() => {
    nextSlide()
  }, 3500)
}

function pauseCarousel() {
  stopCarousel()
}

function stopCarousel() {
  if (carouselTimer) {
    clearInterval(carouselTimer)
    carouselTimer = null
  }
}

const filteredProducts = computed(() => {
  if (activeTab.value === 'featured') {
    return allProducts.value.filter((p) => p.is_featured)
  }
  if (activeTab.value === 'sale') {
    return allProducts.value.filter((p) => p.sale_price && p.sale_price < p.price)
  }
  return allProducts.value
})

function filterProducts(tab) {
  activeTab.value = tab
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    copiedCode.value = code
    setTimeout(() => {
      copiedCode.value = ''
    }, 2000)
  })
}

onMounted(async () => {
  try {
    const [prodRes, categoryRes, promoRes] = await Promise.all([
      productApi.list({ page_size: 16 }),
      productApi.categories(),
      productApi.promotions({ active_only: true }),
    ])
    allProducts.value = prodRes.data.items || []
    categories.value = categoryRes.data || []
    promotions.value = promoRes.data || []
    startCarousel()
  } catch (error) {
    console.error('Lỗi khi tải dữ liệu trang chủ:', error)
  }
})

onUnmounted(() => {
  stopCarousel()
})
</script>

<style scoped>
.home-page {
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  background: #14171c;
  color: #ffffff;
  padding: 3.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 3rem;
  align-items: center;
}

.hero-left {
  display: flex;
  flex-direction: column;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.8rem, 5vw, 4.2rem);
  font-weight: 700;
  line-height: 1.1;
  margin: 0 0 1rem;
  color: #ffffff;
  letter-spacing: 0.02em;
}

.hero-lead {
  font-size: 1.05rem;
  line-height: 1.6;
  margin: 0 0 2rem;
  color: rgba(255, 255, 255, 0.85);
}

.hero-lead strong {
  color: #f1b34e;
}

.hero-cta-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}

.btn-hero-primary {
  padding: 0.85rem 1.6rem;
  font-size: 0.98rem;
  background: #114b43;
  color: #ffffff;
  border: 1px solid #1a6b60;
  border-radius: 999px;
}

.btn-hero-primary:hover {
  background: #0d3b34;
}

.btn-hero-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.4rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hero-ghost:hover {
  background: rgba(255, 255, 255, 0.2);
}

.badge-hot {
  background: #dc2626;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item strong {
  font-size: 1.15rem;
  color: #ffffff;
}

.stat-item span {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.7);
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.15);
}

/* Right side banner card */
.hero-right {
  position: relative;
  width: 100%;
}

.hero-banner-card-wrapper {
  position: relative;
  background: #1f242b;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.hero-banner-card-wrapper:hover {
  border-color: rgba(255, 255, 255, 0.3);
}

.hero-banner-card {
  display: block;
  text-decoration: none;
  color: #ffffff;
  position: relative;
}

.banner-img-box {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #2b303a;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.hero-banner-card-wrapper:hover .banner-img {
  transform: scale(1.04);
}

.banner-badge-row {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 0.5rem;
  z-index: 2;
}

.banner-tag {
  background: #b91c1c;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 9px;
  border-radius: 6px;
  letter-spacing: 0.03em;
}

.banner-sale-tag {
  background: #047857;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}

.banner-info-overlay {
  padding: 1.25rem;
  background: #1a1e24;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.banner-cat {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #f1b34e;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}

.banner-title {
  font-family: var(--font-body);
  font-size: 1.15rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 0.8rem;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.banner-price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.banner-prices {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.banner-sale-price {
  color: #ef4444;
  font-size: 1.2rem;
  font-weight: 800;
}

.banner-old-price {
  color: #9ca3af;
  text-decoration: line-through;
  font-size: 0.9rem;
}

.banner-btn-view {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6ee7b7;
  transition: transform 0.2s ease;
}

.hero-banner-card-wrapper:hover .banner-btn-view {
  transform: translateX(3px);
}

.banner-nav {
  position: absolute;
  top: 38%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  line-height: 1;
  cursor: pointer;
  z-index: 5;
  transition: all 0.2s ease;
}

.banner-nav:hover {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-50%) scale(1.1);
}

.banner-nav.prev {
  left: 10px;
}

.banner-nav.next {
  right: 10px;
}

.banner-dots {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  z-index: 5;
}

.dot-btn {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  padding: 0;
  transition: all 0.25s ease;
}

.dot-btn.active {
  background: #f1b34e;
  width: 20px;
  border-radius: 999px;
}

/* Header Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.view-all-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--accent);
  transition: transform 0.2s ease;
}

.view-all-link:hover {
  transform: translateX(4px);
}

/* Category Grid */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.4rem;
}

.category-card {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.8rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--accent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow);
  border-color: rgba(17, 75, 67, 0.3);
}

.category-card:hover::before {
  opacity: 1;
}

.category-tag {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-gold);
  font-weight: 700;
}

.category-name {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0.4rem 0 0.5rem;
  color: var(--ink);
}

.category-desc {
  font-size: 0.88rem;
  color: var(--muted);
  line-height: 1.5;
  margin: 0 0 1.2rem;
  flex: 1;
}

.category-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--accent);
  transition: gap 0.2s ease;
}

.category-card:hover .category-cta {
  gap: 0.7rem;
}

/* Product Tabs */
.product-tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(25, 23, 20, 0.06);
  padding: 4px;
  border-radius: 999px;
}

.tab-btn {
  border: none;
  background: transparent;
  padding: 0.5rem 1.2rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: #ffffff;
  color: var(--ink);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.products-more-row {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
}

.btn-lg {
  padding: 0.9rem 2rem;
  font-size: 1rem;
}

/* AI Showcase */
.ai-showcase-section {
  background: linear-gradient(180deg, #ece4d8 0%, #f6f0e6 100%);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.ai-banner {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 3rem;
  align-items: center;
}

.ai-badge {
  display: inline-block;
  background: var(--accent);
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 1rem;
}

.ai-banner h2 {
  font-family: var(--font-display);
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  line-height: 1.2;
  margin: 0 0 1rem;
}

.ai-banner p {
  font-size: 1.02rem;
  color: var(--ink-light);
  line-height: 1.6;
  margin-bottom: 1.2rem;
}

.ai-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--accent);
}

.ai-chat-mockup {
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid var(--line);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.mockup-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.2rem;
  background: var(--accent);
  color: #ffffff;
}

.mockup-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-gold);
  color: #171411;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.mockup-header small {
  display: block;
  font-size: 0.72rem;
  color: #cde6e1;
}

.mockup-body {
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  font-size: 0.9rem;
  background: #faf8f5;
}

.mockup-msg {
  padding: 0.75rem 1rem;
  border-radius: 14px;
  line-height: 1.5;
}

.mockup-msg.user {
  background: #e6f0ed;
  color: var(--ink);
  align-self: flex-end;
  border-bottom-right-radius: 2px;
}

.mockup-msg.assistant {
  background: #ffffff;
  color: var(--ink);
  align-self: flex-start;
  border: 1px solid var(--line);
  border-bottom-left-radius: 2px;
}

/* Promos Section */
.promo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.4rem;
}

.promo-card {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  display: flex;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.promo-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.promo-left {
  background: var(--accent);
  color: #ffffff;
  padding: 1.2rem 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.promo-discount-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.discount-num {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
}

.discount-label {
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  opacity: 0.85;
}

.promo-center {
  padding: 1.1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.promo-center h3 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--ink);
}

.promo-desc {
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0 0 0.8rem;
  line-height: 1.4;
  flex: 1;
}

.promo-code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  border: 1px dashed var(--line-strong);
}

.code-text {
  font-family: monospace;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--accent);
  letter-spacing: 0.05em;
}

.btn-copy {
  border: none;
  background: var(--accent);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-copy:hover {
  background: var(--accent-hover);
}

@keyframes zoomSlow {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.05);
  }
}

@media (max-width: 900px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
  .ai-banner {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .hero {
    min-height: auto;
    padding: 2.5rem 0;
  }
  .hero-title {
    font-size: 2.2rem;
  }
  .hero-cta-row {
    flex-direction: column;
  }
  .hero-stats {
    flex-wrap: wrap;
    gap: 1rem;
  }
  .stat-divider {
    display: none;
  }
}
</style>
