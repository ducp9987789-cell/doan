<template>
  <RouterLink :to="`/products/${product.id}`" class="product-card">
    <img :src="product.images?.[0] || placeholder" :alt="product.name" />
    <h3>{{ product.name }}</h3>
    <p class="muted">{{ product.category_name }}</p>
    <div class="price">
      <span class="sale">{{ formatPrice(product.sale_price || product.price) }}</span>
      <span v-if="product.sale_price" class="old">{{ formatPrice(product.price) }}</span>
    </div>
  </RouterLink>
</template>

<script setup>
defineProps({
  product: { type: Object, required: true },
})

const placeholder = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}
</script>
