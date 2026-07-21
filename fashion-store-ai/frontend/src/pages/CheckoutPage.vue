<template>
  <section class="section">
    <div class="container">
      <h1 class="section-title">Checkout</h1>
      <p class="section-desc">Enter shipping details and confirm your order.</p>

      <form class="panel form" @submit.prevent="submit">
        <div class="field">
          <label>Full name</label>
          <input v-model="form.full_name" required />
        </div>
        <div class="field">
          <label>Phone</label>
          <input v-model="form.phone" required />
        </div>
        <div class="field">
          <label>Address</label>
          <input v-model="form.address" required />
        </div>
        <div class="field">
          <label>City</label>
          <input v-model="form.city" required />
        </div>
        <div class="field">
          <label>District</label>
          <input v-model="form.district" />
        </div>
        <div class="field">
          <label>Payment method</label>
          <select v-model="paymentMethod">
            <option value="cod">Cash on delivery</option>
            <option value="bank_transfer">Bank transfer</option>
          </select>
        </div>
        <div class="field">
          <label>Promotion code</label>
          <input v-model="promotionCode" placeholder="WELCOME10" />
        </div>
        <div class="field">
          <label>Note</label>
          <textarea v-model="form.note" rows="3" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn" :disabled="loading">{{ loading ? 'Placing...' : 'Place order' }}</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { orderApi } from '../services'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const cart = useCartStore()
const loading = ref(false)
const error = ref('')
const paymentMethod = ref('cod')
const promotionCode = ref('')
const form = reactive({
  full_name: '',
  phone: '',
  address: '',
  city: '',
  district: '',
  note: '',
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await orderApi.createOrder({
      shipping_address: { ...form },
      payment_method: paymentMethod.value,
      promotion_code: promotionCode.value || null,
    })
    cart.reset()
    router.push('/orders')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Checkout failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form {
  max-width: 640px;
}

.error {
  color: var(--danger);
}
</style>
