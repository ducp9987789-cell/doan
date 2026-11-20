<template>
  <div class="profile-page">
    <div class="container py-4">
      <!-- Header tiêu đề trang Profile -->
      <div class="profile-header-card">
        <div class="user-hero-info">
          <div class="avatar-circle">
            {{ userInitials }}
          </div>
          <div class="user-meta">
            <h1 class="user-display-name">{{ cleanName(profileForm.full_name) || 'Khách Hàng' }}</h1>
            <p class="user-email-text">{{ profileForm.email }}</p>
            <div v-if="auth.isAdmin" class="user-tags">
              <span class="role-tag tag-admin">👑 Quản Trị Viên</span>
            </div>
          </div>
        </div>

        <div class="header-quick-links">
          <RouterLink to="/orders" class="btn-orders-link">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
              <path d="M3 6h18" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
            <span>Đơn hàng của tôi</span>
          </RouterLink>
        </div>
      </div>

      <!-- Grid 2 Cột: Thông tin cá nhân & Đổi mật khẩu -->
      <div class="profile-grid">
        <!-- CỘT 1: CHỈNH SỬA THÔNG TIN CÁ NHÂN -->
        <div class="profile-card">
          <div class="card-head">
            <div class="head-icon">👤</div>
            <div>
              <h2 class="card-title">Hồ sơ cá nhân</h2>
              <p class="card-sub">Cập nhật thông tin liên hệ và địa chỉ nhận hàng của bạn</p>
            </div>
          </div>

          <form @submit.prevent="handleUpdateProfile" class="profile-form">
            <!-- Thông báo thành công / lỗi -->
            <div v-if="profileSuccess" class="alert-box alert-success">
              ✓ {{ profileSuccess }}
            </div>
            <div v-if="profileError" class="alert-box alert-danger">
              ⚠️ {{ profileError }}
            </div>

            <div class="form-group">
              <label for="fullName">Họ và tên <span class="required">*</span></label>
              <input
                id="fullName"
                v-model="profileForm.full_name"
                type="text"
                class="form-control"
                placeholder="Nhập họ và tên đầy đủ..."
                required
              />
            </div>

            <div class="form-row-2">
              <div class="form-group">
                <label for="email">Địa chỉ Email <span class="required">*</span></label>
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  class="form-control"
                  placeholder="name@example.com"
                  required
                />
              </div>

              <div class="form-group">
                <label for="phone">Số điện thoại <span class="required">*</span></label>
                <input
                  id="phone"
                  v-model="profileForm.phone"
                  type="tel"
                  class="form-control"
                  placeholder="0912345678"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label for="address">Địa chỉ giao hàng mặc định</label>
              <textarea
                id="address"
                v-model="profileForm.address"
                class="form-control"
                rows="3"
                placeholder="Số nhà, tên đường, phường/xã, quận/huyện, tỉnh/thành phố..."
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-save" :disabled="loadingProfile">
                <span>{{ loadingProfile ? 'Đang lưu...' : '💾 Lưu thay đổi hồ sơ' }}</span>
              </button>
            </div>
          </form>
        </div>

        <!-- CỘT 2: ĐỔI MẬT KHẨU -->
        <div class="profile-card">
          <div class="card-head">
            <div class="head-icon">🔒</div>
            <div>
              <h2 class="card-title">Đổi mật khẩu</h2>
              <p class="card-sub">Quản lý bảo mật và cập nhật mật khẩu đăng nhập mới</p>
            </div>
          </div>

          <form @submit.prevent="handleChangePassword" class="profile-form">
            <!-- Thông báo thành công / lỗi mật khẩu -->
            <div v-if="passwordSuccess" class="alert-box alert-success">
              ✓ {{ passwordSuccess }}
            </div>
            <div v-if="passwordError" class="alert-box alert-danger">
              ⚠️ {{ passwordError }}
            </div>

            <div class="form-group">
              <label for="curPassword">Mật khẩu hiện tại <span class="required">*</span></label>
              <input
                id="curPassword"
                v-model="passwordForm.current_password"
                type="password"
                class="form-control"
                placeholder="Nhập mật khẩu bạn đang sử dụng..."
                required
                autocomplete="current-password"
              />
            </div>

            <div class="form-group">
              <label for="newPassword">Mật khẩu mới <span class="required">*</span></label>
              <input
                id="newPassword"
                v-model="passwordForm.new_password"
                type="password"
                class="form-control"
                placeholder="Tối thiểu 6 ký tự bảo mật..."
                minlength="6"
                required
                autocomplete="new-password"
              />
            </div>

            <div class="form-group">
              <label for="confirmNewPassword">Xác nhận mật khẩu mới <span class="required">*</span></label>
              <input
                id="confirmNewPassword"
                v-model="passwordForm.confirm_new_password"
                type="password"
                class="form-control"
                placeholder="Nhập lại mật khẩu mới..."
                minlength="6"
                required
                autocomplete="new-password"
              />
            </div>

            <div class="password-hints">
              <p>Mật khẩu nên chứa từ 6 ký tự trở lên để tăng cường bảo vệ tài khoản.</p>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-password" :disabled="loadingPassword">
                <span>{{ loadingPassword ? 'Đang cập nhật...' : '🔑 Cập nhật mật khẩu mới' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { authApi } from '../services'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

// Profile Form State
const profileForm = reactive({
  full_name: '',
  email: '',
  phone: '',
  address: '',
})
const loadingProfile = ref(false)
const profileSuccess = ref('')
const profileError = ref('')

// Password Form State
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_new_password: '',
})
const loadingPassword = ref(false)
const passwordSuccess = ref('')
const passwordError = ref('')

function cleanName(str) {
  return (str || '').replace(/\s*\(Khách Hàng VIP\)/gi, '').trim()
}

const userInitials = computed(() => {
  const name = cleanName(profileForm.full_name || auth.user?.full_name || '')
  return name.trim() ? name.trim().charAt(0).toUpperCase() : 'U'
})

function formatMemberDate(dateStr) {
  if (!dateStr) return 'Gần đây'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('vi-VN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return 'Gần đây'
  }
}

async function loadProfile() {
  try {
    const { data } = await authApi.me()
    profileForm.full_name = cleanName(data.full_name || '')
    profileForm.email = data.email || ''
    profileForm.phone = data.phone || ''
    profileForm.address = data.address || ''

    // Đồng bộ lại vào auth store
    auth.user = { ...data, full_name: profileForm.full_name }
    localStorage.setItem('fs_user', JSON.stringify(auth.user))
  } catch {
    if (auth.user) {
      profileForm.full_name = cleanName(auth.user.full_name || '')
      profileForm.email = auth.user.email || ''
      profileForm.phone = auth.user.phone || ''
      profileForm.address = auth.user.address || ''
    }
  }
}

async function handleUpdateProfile() {
  profileError.value = ''
  profileSuccess.value = ''
  loadingProfile.value = true

  try {
    const payload = {
      full_name: profileForm.full_name.trim(),
      email: profileForm.email.trim(),
      phone: profileForm.phone.trim(),
      address: profileForm.address ? profileForm.address.trim() : '',
    }
    const { data } = await authApi.updateProfile(payload)
    auth.user = data
    localStorage.setItem('fs_user', JSON.stringify(data))

    profileSuccess.value = 'Đã cập nhật thông tin hồ sơ cá nhân thành công!'
    setTimeout(() => {
      profileSuccess.value = ''
    }, 4000)
  } catch (err) {
    profileError.value = err.response?.data?.detail || 'Không thể cập nhật hồ sơ cá nhân. Vui lòng thử lại.'
  } finally {
    loadingProfile.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.new_password !== passwordForm.confirm_new_password) {
    passwordError.value = 'Mật khẩu mới và mật khẩu xác nhận không trùng khớp!'
    return
  }

  if (passwordForm.new_password.length < 6) {
    passwordError.value = 'Mật khẩu mới phải có tối thiểu 6 ký tự.'
    return
  }

  loadingPassword.value = true
  try {
    const payload = {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    }
    const { data } = await authApi.changePassword(payload)
    passwordSuccess.value = data.message || 'Đổi mật khẩu thành công!'

    // Reset password fields
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_new_password = ''

    setTimeout(() => {
      passwordSuccess.value = ''
    }, 4500)
  } catch (err) {
    passwordError.value = err.response?.data?.detail || 'Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu hiện tại.'
  } finally {
    loadingPassword.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  background-color: #f8fafc;
  min-height: calc(100vh - 140px);
  padding: 2rem 0 4rem;
}

.profile-header-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.6rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.user-hero-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar-circle {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0f766e, #14b8a6);
  color: white;
  font-size: 1.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(20, 184, 166, 0.3);
}

.user-display-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.2rem;
}

.user-email-text {
  font-size: 0.95rem;
  color: #64748b;
  margin-bottom: 0.4rem;
}

.user-tags {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  flex-wrap: wrap;
}

.role-tag {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
}

.tag-customer {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.tag-admin {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.date-tag {
  font-size: 0.78rem;
  color: #94a3b8;
}

.btn-orders-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #f1f5f9;
  color: #334155;
  padding: 0.6rem 1.1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.btn-orders-link:hover {
  background: #0f766e;
  color: white;
  border-color: #0f766e;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

.profile-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.75rem 2rem;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.card-head {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.head-icon {
  font-size: 1.6rem;
  background: #f8fafc;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
}

.card-sub {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
}

.required {
  color: #ef4444;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 600px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }
}

.form-control {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.92rem;
  color: #0f172a;
  background: #ffffff;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-control:focus {
  border-color: #0f766e;
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.password-hints {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
  margin-top: -0.25rem;
}

.alert-box {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 500;
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-danger {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.form-actions {
  margin-top: 0.5rem;
}

.btn-save, .btn-password {
  width: 100%;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-save {
  background: #0f766e;
  color: white;
}

.btn-save:hover {
  background: #115e59;
}

.btn-password {
  background: #1e293b;
  color: white;
}

.btn-password:hover {
  background: #0f172a;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

