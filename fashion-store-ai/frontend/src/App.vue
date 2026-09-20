<template>
  <div
    class="app-shell"
    :class="{
      'auth-page-layout': isAuthPage,
      'admin-page-layout': isAdminPage
    }"
  >
    <AppHeader v-if="!isAuthPage && !isAdminPage" />
    <main
      class="main-content"
      :class="{
        'auth-main': isAuthPage,
        'admin-main-wrap': isAdminPage
      }"
    >
      <RouterView />
    </main>
    <ChatWidget v-if="!isAuthPage && !isAdminPage" />
    <AppFooter v-if="!isAuthPage && !isAdminPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppFooter from './components/AppFooter.vue'
import AppHeader from './components/AppHeader.vue'
import ChatWidget from './components/ChatWidget.vue'

const route = useRoute()
const isAuthPage = computed(() => route.name === 'login' || route.meta?.hideLayout)
const isAdminPage = computed(() => route.name === 'admin' || route.path.startsWith('/admin'))
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

.auth-page-layout {
  background:
    radial-gradient(circle at 15% 15%, rgba(17, 75, 67, 0.12), transparent 40%),
    radial-gradient(circle at 85% 85%, rgba(201, 147, 66, 0.14), transparent 40%),
    linear-gradient(180deg, #f7f3eb 0%, #ece4d7 100%);
}

.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2.5rem 1rem;
}

.admin-main-wrap {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
