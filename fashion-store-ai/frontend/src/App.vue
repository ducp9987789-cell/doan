<template>
  <div class="app-shell">
    <AppHeader />
    <main>
      <RouterView />
    </main>
    <ChatWidget />
    <footer class="site-footer">
      <div class="container footer-inner">
        <div>
          <strong class="brand">LUMIA</strong>
          <p class="muted">Fashion store with AI shopping assistant.</p>
        </div>
        <p class="muted">© {{ year }} Fashion Store AI</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import ChatWidget from './components/ChatWidget.vue'

const year = new Date().getFullYear()
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.site-footer {
  border-top: 1px solid var(--line);
  padding: 2rem 0;
  margin-top: 2rem;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
}

.brand {
  font-family: var(--font-display);
  font-size: 1.8rem;
}
</style>
