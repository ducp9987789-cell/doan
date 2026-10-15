<template>
  <div class="auth-wrapper">
    <!-- Phía trên: Tên cửa hàng Fashion Store -->
    <div class="auth-brand-top">
      <RouterLink to="/" class="brand-link" title="Về trang chủ Fashion Store">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
    </div>

    <!-- Khối Form Đăng nhập / Đăng ký -->
    <div class="auth-card panel fade-up">
      <div class="auth-header">
        <h1 class="auth-title">
          {{ mode === 'login' ? 'Đăng nhập' : 'Đăng ký tài khoản' }}
        </h1>
        <p class="auth-subtitle">
          {{ mode === 'login' ? 'Chào mừng bạn quay trở lại với Fashion Store' : 'Tạo tài khoản mới để nhận ngập tràn ưu đãi mua sắm' }}
        </p>
      </div>

      <form class="auth-form" @submit.prevent="submit">
        <!-- Họ tên (Đăng ký) -->
        <div v-if="mode === 'register'" class="field">
          <label>Họ và tên *</label>
          <input
            v-model="form.full_name"
            placeholder="Ví dụ: Nguyễn Văn An"
            required
            autocomplete="name"
          />
        </div>

        <!-- Số điện thoại (Đăng ký) -->
        <div v-if="mode === 'register'" class="field">
          <label>Số điện thoại *</label>
          <input
            v-model="form.phone"
            type="tel"
            placeholder="Ví dụ: 0912345678"
            required
            pattern="[0-9]{10,11}"
            title="Vui lòng nhập số điện thoại hợp lệ (10-11 chữ số)"
            autocomplete="tel"
          />
        </div>

        <!-- Email -->
        <div class="field">
          <label>Địa chỉ Email *</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="name@example.com"
            required
            autocomplete="email"
          />
        </div>

        <!-- Mật khẩu -->
        <div class="field">
          <label>Mật khẩu *</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            required
            minlength="6"
            autocomplete="current-password"
          />
        </div>

        <!-- Xác nhận lại mật khẩu (Đăng ký) -->
        <div v-if="mode === 'register'" class="field">
          <label>Xác nhận lại mật khẩu *</label>
          <input
            v-model="form.confirm_password"
            type="password"
            placeholder="Nhập lại mật khẩu"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>

        <!-- Thông báo lỗi -->
        <div v-if="errorMessage || auth.error" class="error-alert">
          {{ errorMessage || auth.error }}
        </div>

        <!-- Nút submit -->
        <button class="btn btn-block btn-submit" :disabled="auth.loading">
          <span>{{ auth.loading ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập' : 'Đăng ký ngay' }}</span>
        </button>
      </form>

      <!-- Chuyển đổi giữa Đăng nhập / Đăng ký -->
      <div class="auth-switch-box">
        <button class="btn-switch" @click="toggleMode" type="button">
          {{ mode === 'login' ? 'Chưa có tài khoản? Đăng ký ngay' : 'Đã có tài khoản? Đăng nhập' }}
        </button>
      </div>
    </div>

    <!-- Dưới form là nút/link về trang chủ -->
    <div class="back-home-box">
      <RouterLink to="/" class="btn-back-home">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        <span>Về trang chủ</span>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mode = ref(route.query.tab === 'register' ? 'register' : 'login')
const errorMessage = ref('')

const form = reactive({
  full_name: '',
  phone: '',
  email: '',
  password: '',
  confirm_password: '',
})

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  errorMessage.value = ''
  auth.error = ''
}

async function submit() {
  errorMessage.value = ''
  auth.error = ''

  if (mode.value === 'register') {
    if (form.password !== form.confirm_password) {
      errorMessage.value = 'Mật khẩu xác nhận không khớp. Vui lòng nhập lại.'
      return
    }
  }

  try {
    if (mode.value === 'login') {
      await auth.login(form.email, form.password)
    } else {
      await auth.register({
        full_name: form.full_name,
        phone: form.phone,
        email: form.email,
        password: form.password,
      })
    }
    if (auth.isAdmin) {
      router.push('/admin')
    } else {
      const redirectUrl = (route.query.redirect && route.query.redirect !== '/') ? route.query.redirect : '/products'
      router.push(redirectUrl)
    }
  } catch (err) {
    console.error('Lỗi xác thực:', err)
  }
}

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'register') {
      mode.value = 'register'
    } else {
      mode.value = 'login'
    }
  }
)

onMounted(() => {
  if (route.query.tab === 'register') {
    mode.value = 'register'
  }
})
</script>

<style scoped>
.auth-wrapper {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Phần trên cùng: Tên cửa hàng */
.auth-brand-top {
  margin-bottom: 1.8rem;
  text-align: center;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  text-decoration: none;
}

.brand-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: var(--accent);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(17, 75, 67, 0.3);
  transition: transform 0.25s ease;
}

.brand-link:hover .brand-icon {
  transform: rotate(-6deg) scale(1.06);
}

.brand-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ink);
  line-height: 1;
}

.brand-sub {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent-gold);
  font-weight: 700;
  margin-top: 2px;
}

/* Form Card */
.auth-card {
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 2.2rem;
  box-shadow: 0 20px 50px rgba(25, 23, 20, 0.08);
  border: 1px solid var(--line);
}

.auth-header {
  text-align: center;
  margin-bottom: 1.6rem;
}

.auth-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.4rem;
}

.auth-subtitle {
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.4;
}

.error-alert {
  padding: 0.8rem 1rem;
  background: var(--danger-soft);
  color: var(--danger);
  border-radius: 10px;
  font-size: 0.86rem;
  font-weight: 600;
  margin-bottom: 1.1rem;
}

.btn-submit {
  padding: 0.95rem;
  font-size: 1.05rem;
  margin-top: 0.6rem;
  border-radius: 999px;
}

.btn-block {
  width: 100%;
}

.auth-switch-box {
  margin-top: 1.4rem;
  text-align: center;
  border-top: 1px solid var(--line);
  padding-top: 1.1rem;
}

.btn-switch {
  border: none;
  background: transparent;
  color: var(--accent);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.btn-switch:hover {
  text-decoration: underline;
  color: var(--accent-hover);
}

/* Dưới form: Về trang chủ */
.back-home-box {
  margin-top: 1.5rem;
  text-align: center;
}

.btn-back-home {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--muted);
  font-size: 0.92rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--line);
}

.btn-back-home:hover {
  color: var(--ink);
  background: #ffffff;
  border-color: var(--ink);
  transform: translateX(-3px);
}

@media (max-width: 520px) {
  .auth-card {
    padding: 1.6rem;
  }
}
</style>
