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

    <!-- Khối Form Đăng nhập / Đăng ký / Quên mật khẩu -->
    <div class="auth-card panel fade-up">
      <div class="auth-header">
        <h1 class="auth-title">
          {{ mode === 'login' ? 'Đăng nhập' : mode === 'register' ? 'Đăng ký tài khoản' : 'Khôi phục mật khẩu' }}
        </h1>
        <p class="auth-subtitle">
          {{ mode === 'login' ? 'Chào mừng bạn quay trở lại với Fashion Store' : mode === 'register' ? 'Tạo tài khoản mới để nhận ngập tràn ưu đãi mua sắm' : 'Nhập email hoặc số điện thoại đã đăng ký để nhận mã OTP' }}
        </p>
      </div>

      <!-- FORM ĐĂNG NHẬP HOẶC ĐĂNG KÝ -->
      <form v-if="mode !== 'forgot'" class="auth-form" @submit.prevent="submit">
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

        <!-- Email (Đăng nhập) -->
        <div v-if="mode === 'login'" class="field">
          <label>Địa chỉ Email *</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="name@example.com"
            required
            autocomplete="email"
          />
        </div>

        <!-- Email có nút gửi OTP (Đăng ký) -->
        <div v-if="mode === 'register'" class="field">
          <label>Địa chỉ Email nhận mã OTP *</label>
          <div class="input-with-button">
            <input
              v-model="form.email"
              type="email"
              placeholder="name@gmail.com"
              required
              :disabled="registerOtpCountdown > 0"
              autocomplete="email"
            />
            <button
              type="button"
              class="btn-inline-action"
              :disabled="registerLoadingOtp || registerOtpCountdown > 0 || !form.email.trim()"
              @click="handleSendRegisterOtp"
            >
              {{ registerOtpCountdown > 0 ? `${registerOtpCountdown}s` : registerLoadingOtp ? 'Đang gửi...' : registerOtpSent ? 'Gửi lại OTP' : 'Gửi mã OTP' }}
            </button>
          </div>
        </div>

        <!-- Thông báo OTP đăng ký đã gửi -->
        <div v-if="mode === 'register' && registerOtpMessage" class="alert-info-box">
          {{ registerOtpMessage }}
        </div>

        <!-- Ô nhập mã OTP khi đăng ký -->
        <div v-if="mode === 'register'" class="field">
          <label>Mã xác thực OTP gửi về Gmail *</label>
          <div class="input-with-button">
            <input
              v-model="form.otp"
              type="text"
              placeholder="Nhập mã 6 chữ số..."
              maxlength="6"
              required
              :disabled="!registerOtpSent"
            />
            <button
              type="button"
              class="btn-inline-action btn-verify-action"
              :class="{ 'btn-verified': registerOtpVerified }"
              :disabled="registerOtpVerified || registerLoadingVerify || !form.otp?.trim()"
              @click="handleVerifyRegisterOtp"
            >
              {{ registerOtpVerified ? '✓ Đã khớp' : registerLoadingVerify ? 'Đang kiểm tra...' : 'Kiểm tra OTP' }}
            </button>
          </div>
          <small v-if="registerOtpVerified" class="text-success-hint">✓ Mã OTP hợp lệ. Hãy bấm "Xác nhận & Đăng ký" bên dưới.</small>
          <small v-else-if="registerOtpSent && registerOtpCountdown > 0" class="text-muted-hint">⏱️ Mã có hiệu lực trong 1 phút (còn {{ registerOtpCountdown }}s). Vui lòng kiểm tra hộp thư Gmail.</small>
          <small v-else-if="registerOtpSent && registerOtpCountdown === 0" class="text-danger-hint">⚠️ Mã OTP đã hết hạn 1 phút. Hãy bấm "Gửi lại OTP" để nhận mã mới.</small>
          <small v-else class="text-muted-hint">Nhập Gmail rồi bấm "Gửi mã OTP" để nhận mã xác thực qua email.</small>
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
        <button class="btn btn-block btn-submit" :disabled="auth.loading || (mode === 'register' && (!registerOtpSent || !form.otp))">
          <span>{{ auth.loading ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập' : 'Xác nhận & Đăng ký ngay' }}</span>
        </button>
      </form>

      <!-- FORM QUÊN MẬT KHẨU (OTP + RESET MẬT KHẨU) -->
      <form v-else class="auth-form" @submit.prevent="submitResetPassword">
        <!-- 1. Email hoặc Số điện thoại -->
        <div class="field">
          <label>Email hoặc Số điện thoại đăng ký *</label>
          <div class="input-with-button">
            <input
              v-model="forgotForm.email_or_phone"
              type="text"
              placeholder="Nhập email hoặc số điện thoại..."
              required
              :disabled="isOtpVerified"
            />
            <button
              type="button"
              class="btn-inline-action"
              :disabled="loadingOtp || otpCountdown > 0 || !forgotForm.email_or_phone.trim()"
              @click="handleSendOtp"
            >
              {{ otpCountdown > 0 ? `${otpCountdown}s` : loadingOtp ? 'Đang gửi...' : 'Gửi mã OTP' }}
            </button>
          </div>
        </div>

        <!-- Thông báo OTP đã gửi -->
        <div v-if="otpSentMessage" class="alert-info-box">
          {{ otpSentMessage }}
        </div>

        <!-- 2. Ô nhập mã OTP -->
        <div class="field">
          <label>Mã xác thực OTP *</label>
          <div class="input-with-button">
            <input
              v-model="forgotForm.otp"
              type="text"
              placeholder="Nhập mã 6 chữ số..."
              maxlength="6"
              required
              :disabled="isOtpVerified || !otpSent"
            />
            <button
              type="button"
              class="btn-inline-action btn-verify-action"
              :class="{ 'btn-verified': isOtpVerified }"
              :disabled="isOtpVerified || loadingVerify || !forgotForm.otp.trim()"
              @click="handleVerifyOtp"
            >
              {{ isOtpVerified ? '✓ Đã khớp' : loadingVerify ? 'Đang kiểm tra...' : 'Xác thực OTP' }}
            </button>
          </div>
          <small v-if="isOtpVerified" class="text-success-hint">✓ Mã OTP hợp lệ. Bây giờ bạn có thể nhập mật khẩu mới phía dưới.</small>
          <small v-else-if="!otpSent" class="text-muted-hint">Bấm "Gửi mã OTP" để nhận mã xác nhận.</small>
        </div>

        <!-- 3. Mật khẩu mới (Khóa cho đến khi xác thực OTP thành công) -->
        <div class="field" :class="{ 'field-locked': !isOtpVerified }">
          <label>Mật khẩu mới *</label>
          <input
            v-model="forgotForm.new_password"
            type="password"
            placeholder="Tối thiểu 6 ký tự..."
            minlength="6"
            required
            :disabled="!isOtpVerified"
            autocomplete="new-password"
          />
        </div>

        <!-- 4. Xác nhận lại mật khẩu mới -->
        <div class="field" :class="{ 'field-locked': !isOtpVerified }">
          <label>Xác nhận lại mật khẩu mới *</label>
          <input
            v-model="forgotForm.confirm_password"
            type="password"
            placeholder="Nhập lại mật khẩu mới..."
            minlength="6"
            required
            :disabled="!isOtpVerified"
            autocomplete="new-password"
          />
        </div>

        <!-- Thông báo lỗi / thành công khi reset -->
        <div v-if="forgotSuccess" class="alert-success-box">
          ✓ {{ forgotSuccess }}
        </div>
        <div v-if="forgotError" class="error-alert">
          {{ forgotError }}
        </div>

        <!-- Nút Đặt lại mật khẩu -->
        <button class="btn btn-block btn-submit" :disabled="!isOtpVerified || loadingReset">
          <span>{{ loadingReset ? 'Đang đặt lại mật khẩu...' : 'Đặt lại mật khẩu mới' }}</span>
        </button>
      </form>

      <!-- Dòng chuyển đổi Đăng nhập / Đăng ký / Quên mật khẩu -->
      <div v-if="mode !== 'forgot'" class="auth-switch-box">
        <button class="btn-switch" @click="toggleMode" type="button">
          {{ mode === 'login' ? 'Đăng ký ngay' : 'Đăng nhập' }}
        </button>
        <button v-if="mode === 'login'" class="btn-switch btn-forgot-link" @click="openForgotMode" type="button">
          Quên mật khẩu?
        </button>
      </div>

      <div v-else class="auth-switch-box">
        <button class="btn-switch btn-back-login" @click="backToLogin" type="button">
          ← Quay lại Đăng nhập
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
import { authApi } from '../services'

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
  otp: '',
})

// State cho đăng ký OTP
const registerOtpSent = ref(false)
const registerOtpMessage = ref('')
const registerOtpCountdown = ref(0)
let registerCountdownTimer = null
const registerOtpVerified = ref(false)
const registerLoadingOtp = ref(false)
const registerLoadingVerify = ref(false)

function startRegisterCountdown(seconds = 60) {
  registerOtpCountdown.value = seconds
  if (registerCountdownTimer) clearInterval(registerCountdownTimer)
  registerCountdownTimer = setInterval(() => {
    if (registerOtpCountdown.value > 0) {
      registerOtpCountdown.value--
    } else {
      clearInterval(registerCountdownTimer)
      registerCountdownTimer = null
    }
  }, 1000)
}

async function handleSendRegisterOtp() {
  errorMessage.value = ''
  registerOtpMessage.value = ''
  if (!form.email || !form.email.includes('@')) {
    errorMessage.value = 'Vui lòng nhập địa chỉ email hợp lệ trước khi gửi mã OTP.'
    return
  }
  registerLoadingOtp.value = true
  try {
    const res = await authApi.sendRegisterOtp({ email: form.email.trim() })
    registerOtpSent.value = true
    startRegisterCountdown(60)
    registerOtpMessage.value = res.data?.message || 'Mã OTP đã được gửi đến email của bạn!'
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Lỗi khi gửi mã OTP. Vui lòng kiểm tra lại email.'
  } finally {
    registerLoadingOtp.value = false
  }
}

async function handleVerifyRegisterOtp() {
  errorMessage.value = ''
  if (!form.otp || !form.otp.trim()) {
    errorMessage.value = 'Vui lòng nhập mã OTP 6 chữ số gửi về email.'
    return
  }
  registerLoadingVerify.value = true
  try {
    const res = await authApi.verifyRegisterOtp({ email: form.email.trim(), otp: form.otp.trim() })
    registerOtpVerified.value = true
    registerOtpMessage.value = '✓ ' + (res.data?.message || 'Xác thực email thành công!')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Mã OTP không chính xác hoặc đã hết hạn.'
  } finally {
    registerLoadingVerify.value = false
  }
}

// State cho chức năng Quên mật khẩu & OTP
const forgotForm = reactive({
  email_or_phone: '',
  otp: '',
  new_password: '',
  confirm_password: '',
})
const otpSent = ref(false)
const otpSentMessage = ref('')
const otpCountdown = ref(0)
let countdownTimer = null
const isOtpVerified = ref(false)
const loadingOtp = ref(false)
const loadingVerify = ref(false)
const loadingReset = ref(false)
const forgotSuccess = ref('')
const forgotError = ref('')

function openForgotMode() {
  mode.value = 'forgot'
  errorMessage.value = ''
  auth.error = ''
  forgotError.value = ''
  forgotSuccess.value = ''
  isOtpVerified.value = false
  otpSent.value = false
  otpSentMessage.value = ''
}

function backToLogin() {
  mode.value = 'login'
  errorMessage.value = ''
  auth.error = ''
  forgotError.value = ''
  forgotSuccess.value = ''
}

function startCountdown(seconds = 60) {
  otpCountdown.value = seconds
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (otpCountdown.value > 0) {
      otpCountdown.value--
    } else {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

async function handleSendOtp() {
  forgotError.value = ''
  forgotSuccess.value = ''
  otpSentMessage.value = ''
  if (!forgotForm.email_or_phone.trim()) {
    forgotError.value = 'Vui lòng nhập email hoặc số điện thoại.'
    return
  }
  loadingOtp.value = true
  try {
    const res = await authApi.sendForgotOtp({ email_or_phone: forgotForm.email_or_phone.trim() })
    otpSent.value = true
    startCountdown(60)
    otpSentMessage.value = res.data?.message || 'Mã xác thực OTP đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư!'
  } catch (err) {
    forgotError.value = err.response?.data?.detail || 'Không tìm thấy tài khoản với thông tin này hoặc có lỗi xảy ra.'
  } finally {
    loadingOtp.value = false
  }
}

async function handleVerifyOtp() {
  forgotError.value = ''
  forgotSuccess.value = ''
  if (!forgotForm.otp.trim()) {
    forgotError.value = 'Vui lòng nhập mã OTP 6 chữ số.'
    return
  }
  loadingVerify.value = true
  try {
    const res = await authApi.verifyForgotOtp({ email_or_phone: forgotForm.email_or_phone.trim(), otp: forgotForm.otp.trim() })
    isOtpVerified.value = true
    forgotSuccess.value = res.data?.message || 'Xác thực mã OTP thành công!'
  } catch (err) {
    forgotError.value = err.response?.data?.detail || 'Mã OTP không chính xác hoặc đã hết hạn.'
  } finally {
    loadingVerify.value = false
  }
}

async function submitResetPassword() {
  forgotError.value = ''
  forgotSuccess.value = ''
  if (!isOtpVerified.value) {
    forgotError.value = 'Vui lòng xác thực mã OTP trước khi đặt mật khẩu mới.'
    return
  }
  if (forgotForm.new_password !== forgotForm.confirm_password) {
    forgotError.value = 'Mật khẩu xác nhận không khớp.'
    return
  }
  if (forgotForm.new_password.length < 6) {
    forgotError.value = 'Mật khẩu mới phải có ít nhất 6 ký tự.'
    return
  }
  loadingReset.value = true
  try {
    const res = await authApi.resetPassword({
      email_or_phone: forgotForm.email_or_phone.trim(),
      otp: forgotForm.otp.trim(),
      new_password: forgotForm.new_password,
      confirm_password: forgotForm.confirm_password,
    })
    forgotSuccess.value = (res.data?.message || 'Đặt lại mật khẩu thành công!') + ' Đang chuyển về đăng nhập...'
    setTimeout(() => {
      mode.value = 'login'
      form.email = forgotForm.email_or_phone.includes('@') ? forgotForm.email_or_phone : ''
      forgotForm.otp = ''
      forgotForm.new_password = ''
      forgotForm.confirm_password = ''
      isOtpVerified.value = false
      otpSent.value = false
      otpSentMessage.value = ''
      forgotSuccess.value = ''
    }, 2000)
  } catch (err) {
    forgotError.value = err.response?.data?.detail || 'Đặt lại mật khẩu thất bại. Vui lòng thử lại.'
  } finally {
    loadingReset.value = false
  }
}

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  errorMessage.value = ''
  auth.error = ''
  registerOtpSent.value = false
  registerOtpVerified.value = false
  registerOtpMessage.value = ''
  form.otp = ''
}

async function submit() {
  errorMessage.value = ''
  auth.error = ''

  if (mode.value === 'register') {
    if (!form.otp || !form.otp.trim()) {
      errorMessage.value = 'Vui lòng bấm "Gửi mã OTP" và nhập mã OTP 6 chữ số đã được gửi về Gmail của bạn.'
      return
    }
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
        otp: form.otp,
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.8rem;
  border-top: 1px solid var(--line);
  padding-top: 1.1rem;
}

.btn-switch {
  border: none;
  background: transparent;
  color: var(--accent);
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 0;
}

.btn-switch:hover {
  text-decoration: underline;
  color: var(--accent-hover);
}

.btn-forgot-link {
  color: var(--muted);
  font-weight: 600;
}

.btn-forgot-link:hover {
  color: var(--accent);
}

.btn-back-login {
  color: var(--ink);
  font-weight: 700;
}

/* Input group with inline action button */
.input-with-button {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
}

.input-with-button input {
  flex: 1;
}

.btn-inline-action {
  background: var(--accent);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-sm, 8px);
  padding: 0 1rem;
  font-size: 0.84rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-inline-action:hover:not(:disabled) {
  background: var(--accent-hover, #0d3b34);
}

.btn-inline-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-verify-action {
  background: var(--surface-variant, #2a2825);
}

.btn-verify-action.btn-verified {
  background: #10b981 !important;
  color: #ffffff !important;
  opacity: 1 !important;
  cursor: default;
}

.field-locked {
  opacity: 0.75;
}

.field-locked input {
  background: #f8fafc;
  cursor: not-allowed;
}

.lock-indicator {
  font-size: 0.76rem;
  font-weight: 600;
  color: #f59e0b;
  margin-left: 0.5rem;
}

.text-success-hint {
  display: block;
  font-size: 0.78rem;
  color: #10b981;
  font-weight: 600;
  margin-top: 0.35rem;
}

.text-muted-hint {
  display: block;
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: 0.35rem;
}

.text-danger-hint {
  display: block;
  font-size: 0.78rem;
  color: #dc2626;
  font-weight: 600;
  margin-top: 0.35rem;
}

.alert-info-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 1.1rem;
  line-height: 1.4;
}

.alert-success-box {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.86rem;
  font-weight: 600;
  margin-bottom: 1.1rem;
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
