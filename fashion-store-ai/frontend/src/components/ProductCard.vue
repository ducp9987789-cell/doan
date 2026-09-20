<template>
  <RouterLink :to="`/products/${product.id}`" class="product-card" :title="product.name">
    <div class="img-wrapper">
      <img :src="product.images?.[0] || placeholder" :alt="product.name" loading="lazy" />
      
      <!-- Giảm giá % badge -->
      <span v-if="discountPercent" class="badge-sale">-{{ discountPercent }}%</span>
      
      <!-- Nổi bật badge -->
      <span v-else-if="product.is_featured" class="badge-featured">Hot</span>
      
      <!-- Nút xem nhanh khi hover -->
      <div class="card-overlay">
        <span class="btn-quick-view">Xem chi tiết</span>
      </div>
    </div>

    <div class="card-body">
      <span class="category-name">{{ product.category_name || 'Thời trang' }}</span>
      <h3>{{ product.name }}</h3>
      
      <div class="card-footer">
        <div class="price">
          <span class="sale">{{ formatPrice(product.sale_price || product.price) }}</span>
          <span v-if="product.sale_price && product.sale_price < product.price" class="old">
            {{ formatPrice(product.price) }}
          </span>
        </div>

        <div v-if="product.colors?.length" class="color-count" title="Số lượng màu sắc">
          {{ product.colors.length }} màu
        </div>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, required: true },
})

const placeholder = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'

const discountPercent = computed(() => {
  if (props.product.sale_price && props.product.price && props.product.sale_price < props.product.price) {
    return Math.round(((props.product.price - props.product.sale_price) / props.product.price) * 100)
  }
  return null
})

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}
</script>

<style scoped>
.product-card {
  position: relative;
  background: #ffffff;
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--line);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  text-decoration: none;
}

.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 36px rgba(25, 23, 20, 0.12);
  border-color: rgba(17, 75, 67, 0.3);
}

.img-wrapper {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4 / 5;
  background: var(--bg-deep);
}

.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover .img-wrapper img {
  transform: scale(1.06);
}

.badge-sale {
  position: absolute;
  top: 10px;
  left: 10px;
  background: var(--danger);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(179, 57, 57, 0.35);
  z-index: 2;
}

.badge-featured {
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--accent);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 9px;
  border-radius: 999px;
  z-index: 2;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(25, 23, 20, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 3;
}

.product-card:hover .card-overlay {
  opacity: 1;
}

.btn-quick-view {
  background: rgba(255, 255, 255, 0.95);
  color: var(--ink);
  font-weight: 700;
  font-size: 0.85rem;
  padding: 0.55rem 1.1rem;
  border-radius: 999px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
  transform: translateY(8px);
  transition: transform 0.3s ease;
}

.product-card:hover .btn-quick-view {
  transform: translateY(0);
}

.card-body {
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.category-name {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-gold);
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.product-card h3 {
  font-family: var(--font-body);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  line-height: 1.4;
  color: var(--ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.8em;
}

.card-footer {
  margin-top: auto;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.5rem;
}

.price {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  flex-wrap: wrap;
}

.price .sale {
  color: var(--accent);
  font-weight: 800;
  font-size: 1.1rem;
}

.price .old {
  color: var(--muted);
  text-decoration: line-through;
  font-size: 0.85rem;
}

.color-count {
  font-size: 0.75rem;
  color: var(--muted);
  background: var(--bg);
  padding: 2px 7px;
  border-radius: 6px;
  white-space: nowrap;
}
</style>
