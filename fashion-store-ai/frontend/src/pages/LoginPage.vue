<template>
  <section class="section">
    <div class="container narrow">
      <h1 class="section-title">{{ mode === 'login' ? 'Sign in' : 'Create account' }}</h1>
      <p class="section-desc">
        Demo admin: admin@fashionstore.local / Admin@123
      </p>

      <form class="panel" @submit.prevent="submit">
        <div v-if="mode === 'register'" class="field">
          <label>Full name</label>
          <input v-model="form.full_name" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="form.email" type="email" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="form.password" type="password" required minlength="6" />
        </div>
        <p v-if="auth.error" class="error">{{ auth.error }}</p>
        <button class="btn" :disabled="auth.loading">
          {{ auth.loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Register' }}
        </button>
      </form>

      <button class="switch" @click="mode = mode === 'login' ? 'register' : 'login'">
        {{ mode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in' }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mode = ref('login')
const form = reactive({
  full_name: '',
  email: '',
  password: '',
})

async function submit() {
  if (mode.value === 'login') {
    await auth.login(form.email, form.password)
  } else {
    await auth.register(form)
  }
  router.push(route.query.redirect || '/')
}
</script>

<style scoped>
.narrow {
  max-width: 520px;
}

.error {
  color: var(--danger);
}

.switch {
  margin-top: 1rem;
  border: 0;
  background: transparent;
  color: var(--accent);
  cursor: pointer;
}
</style>
