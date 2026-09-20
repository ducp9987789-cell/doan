<template>
  <section class="section checkout-page">
    <div class="container">
      <h1 class="section-title">Thanh toán đơn hàng</h1>
      <p class="section-desc">Vui lòng điền thông tin người nhận và lựa chọn phương thức thanh toán phù hợp.</p>

      <form class="panel checkout-form" @submit.prevent="submit">
        <h3 class="form-section-title">1. Thông tin giao hàng</h3>

        <div class="field-row">
          <div class="field">
            <label>Họ và tên người nhận *</label>
            <input v-model="form.full_name" placeholder="Ví dụ: Nguyễn Văn An" required />
          </div>

          <div class="field">
            <label>Số điện thoại liên hệ *</label>
            <input v-model="form.phone" type="tel" placeholder="Ví dụ: 0912345678" required />
          </div>
        </div>

        <div class="field">
          <label>Địa chỉ nhận hàng chi tiết *</label>
          <input v-model="form.address" placeholder="Số nhà, tên đường, tòa nhà..." required />
        </div>

        <div class="field-row">
          <div class="field">
            <label>Tỉnh / Thành phố *</label>
            <input v-model="form.city" placeholder="Ví dụ: TP. Hồ Chí Minh" required />
          </div>

          <div class="field">
            <label>Quận / Huyện</label>
            <input v-model="form.district" placeholder="Ví dụ: Quận 1" />
          </div>
        </div>

        <h3 class="form-section-title mt-4">2. Phương thức thanh toán</h3>
        <div class="field">
          <select v-model="paymentMethod">
            <option value="cod">💵 Thanh toán tiền mặt khi nhận hàng (COD)</option>
            <option value="bank_transfer">💳 Chuyển khoản ngân hàng (QR Code / Internet Banking)</option>
          </select>
        </div>

        <h3 class="form-section-title mt-4">3. Mã khuyến mãi & Ghi chú</h3>
        <div class="field">
          <label>Mã giảm giá (Nếu có)</label>
          <input v-model="promotionCode" placeholder="Nhập mã ví dụ: WELCOME10, FREESHIP, FASHION20" />
        </div>

        <div class="field">
          <label>Ghi chú cho đơn hàng</label>
          <textarea v-model="form.note" rows="3" placeholder="Ghi chú thêm về thời gian giao hàng hoặc chỉ dẫn giao hàng..." />
        </div>

        <div v-if="error" class="error-alert">
          {{ error }}
        </div>

        <div class="submit-action">
          <button class="btn btn-block btn-place-order" :disabled="loading">
            <span>{{ loading ? 'Đang xử lý đặt hàng...' : 'Xác nhận đặt hàng ngay' }}</span>
          </button>
        </div>
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
      promotion_code: promotionCode.value ? promotionCode.value.trim() : null,
    })
    cart.reset()
    router.push('/orders')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Đặt hàng không thành công. Vui lòng kiểm tra lại thông tin.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.checkout-form {
  max-width: 720px;
  background: #ffffff;
  padding: 2.2rem;
  margin: 0 auto;
}

.form-section-title {
  font-family: var(--font-display);
  font-size: 1.4rem;
  color: var(--accent);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--line);
}

.mt-4 {
  margin-top: 1.8rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.error-alert {
  padding: 0.85rem 1rem;
  background: var(--danger-soft);
  color: var(--danger);
  border-radius: 10px;
  font-weight: 600;
  margin-bottom: 1.2rem;
}

.btn-place-order {
  padding: 1rem;
  font-size: 1.05rem;
}

.btn-block {
  width: 100%;
}

@media (max-width: 600px) {
  .field-row {
    grid-template-columns: 1fr;
  }
  .checkout-form {
    padding: 1.4rem;
  }
}
</style>
