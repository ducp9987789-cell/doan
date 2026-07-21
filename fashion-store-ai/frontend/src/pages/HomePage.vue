<template>
  <div>
    <section class="hero">
      <div class="hero-media" aria-hidden="true"></div>
      <div class="container hero-content fade-up">
        <p class="eyebrow">Online fashion boutique</p>
        <h1>LUMIA</h1>
        <p class="lead">Curated wardrobe, AI stylist on call — shop with confidence day or night.</p>
        <div class="cta-row">
          <RouterLink class="btn" to="/products">Shop collection</RouterLink>
          <button class="btn ghost" @click="scrollPromos">View promotions</button>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2 class="section-title">Featured pieces</h2>
        <p class="section-desc">Selected styles ready for everyday looks and office polish.</p>
        <div class="grid-products">
          <ProductCard v-for="item in featured" :key="item.id" :product="item" />
        </div>
      </div>
    </section>

    <section class="section categories">
      <div class="container">
        <h2 class="section-title">Browse by category</h2>
        <p class="section-desc">Find shirts, denim, dresses and accessories in one place.</p>
        <div class="category-row">
          <RouterLink
            v-for="cat in categories"
            :key="cat.id"
            class="category-item"
            :to="{ name: 'products', query: { category_id: cat.id } }"
          >
            <span>{{ cat.name }}</span>
            <small>{{ cat.description }}</small>
          </RouterLink>
        </div>
      </div>
    </section>

    <section id="promos" class="section">
      <div class="container">
        <h2 class="section-title">Promotions</h2>
        <p class="section-desc">Apply codes at checkout to unlock savings.</p>
        <div class="promo-row">
          <article v-for="promo in promotions" :key="promo.id" class="panel promo">
            <h3>{{ promo.title }}</h3>
            <p class="muted">{{ promo.description }}</p>
            <strong>{{ promo.code }}</strong>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import { productApi } from '../services'

const featured = ref([])
const categories = ref([])
const promotions = ref([])

function scrollPromos() {
  document.getElementById('promos')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  const [featuredRes, categoryRes, promoRes] = await Promise.all([
    productApi.list({ featured: true, page_size: 4 }),
    productApi.categories(),
    productApi.promotions(),
  ])
  featured.value = featuredRes.data.items
  categories.value = categoryRes.data
  promotions.value = promoRes.data
})
</script>

<style scoped>
.hero {
  position: relative;
  min-height: calc(100vh - 74px);
  display: grid;
  align-items: end;
  overflow: hidden;
}

.hero-media {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(20, 18, 15, 0.18), rgba(20, 18, 15, 0.55)),
    url('https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1800&q=80')
      center/cover;
  animation: zoomSlow 18s ease-in-out infinite alternate;
}

.hero-content {
  position: relative;
  z-index: 1;
  color: #f7f2ea;
  padding-bottom: 5rem;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.78rem;
  margin-bottom: 0.6rem;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(4.5rem, 12vw, 8.5rem);
  line-height: 0.9;
  margin: 0 0 1rem;
  letter-spacing: 0.04em;
}

.lead {
  max-width: 32rem;
  font-size: 1.1rem;
  margin: 0 0 1.6rem;
  color: rgba(247, 242, 234, 0.88);
}

.cta-row {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.category-row,
.promo-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.category-item {
  padding: 1.4rem;
  border-top: 1px solid var(--line);
  transition: background 0.3s ease, transform 0.3s ease;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.45);
  transform: translateY(-4px);
}

.category-item span {
  display: block;
  font-family: var(--font-display);
  font-size: 2rem;
}

.promo h3 {
  margin-top: 0;
  font-family: var(--font-display);
  font-size: 1.7rem;
}

@keyframes zoomSlow {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.06);
  }
}
</style>
