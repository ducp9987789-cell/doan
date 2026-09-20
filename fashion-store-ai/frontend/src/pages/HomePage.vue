<template>
  <div class="home-page">
    <!-- Hero Banner Thời Trang -->
    <section class="hero">
      <div class="hero-media" aria-hidden="true"></div>
      <div class="hero-overlay"></div>
      <div class="container hero-content fade-up">
        <div class="hero-badge">
          <span class="sparkle">✨</span>
          <span>Bộ sưu tập thời trang cao cấp & Xu hướng mới 2026</span>
        </div>
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
            <strong>100%</strong>
            <span>Hàng chính hãng</span>
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
import { computed, onMounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import { productApi } from '../services'

const allProducts = ref([])
const categories = ref([])
const promotions = ref([])
const activeTab = ref('all')
const copiedCode = ref('')

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
  } catch (error) {
    console.error('Lỗi khi tải dữ liệu trang chủ:', error)
  }
})
</script>

<style scoped>
.home-page {
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  position: relative;
  min-height: calc(88vh - 110px);
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 4rem 0;
}

.hero-media {
  position: absolute;
  inset: 0;
  background: url('https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=2000&q=80') center/cover no-repeat;
  transform: scale(1.02);
  animation: zoomSlow 20s ease-in-out infinite alternate;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(20, 18, 15, 0.78) 0%, rgba(20, 18, 15, 0.52) 100%);
}

.hero-content {
  position: relative;
  z-index: 2;
  color: #ffffff;
  max-width: 780px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 0.45rem 1.1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin-bottom: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #f7f2ea;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(3.2rem, 8vw, 5.8rem);
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.04em;
  margin: 0 0 1.2rem;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.hero-lead {
  font-size: clamp(1.05rem, 2vw, 1.25rem);
  line-height: 1.6;
  margin: 0 0 2rem;
  color: rgba(255, 255, 255, 0.9);
}

.hero-lead strong {
  color: var(--accent-gold);
}

.hero-cta-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2.8rem;
}

.btn-hero-primary {
  padding: 0.95rem 1.8rem;
  font-size: 1.05rem;
  background: var(--accent);
}

.btn-hero-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.95rem 1.6rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.35);
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-hero-ghost:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.badge-hot {
  background: var(--danger);
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
  border-top: 1px solid rgba(255, 255, 255, 0.18);
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item strong {
  font-size: 1.3rem;
  color: #ffffff;
}

.stat-item span {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.75);
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
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
  .ai-banner {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .hero {
    min-height: auto;
    padding: 3rem 0;
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
