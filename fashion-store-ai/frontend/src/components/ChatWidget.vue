<template>
  <div class="chat-root">
    <button class="chat-toggle" @click="open = !open">{{ open ? 'Close' : 'AI Stylist' }}</button>
    <section v-if="open" class="chat-panel panel fade-up">
      <header>
        <h3>LUMIA AI Stylist</h3>
        <p class="muted">Ask about products, sizes, shipping or promotions.</p>
      </header>
      <div class="messages" ref="listRef">
        <div v-for="(msg, idx) in messages" :key="idx" class="msg" :class="msg.role">
          <p>{{ msg.text }}</p>
          <div v-if="msg.products?.length" class="suggestions">
            <RouterLink
              v-for="product in msg.products"
              :key="product.id"
              :to="`/products/${product.id}`"
              class="suggestion"
            >
              {{ product.name }}
            </RouterLink>
          </div>
        </div>
      </div>
      <div class="quick">
        <button v-for="q in quickQuestions" :key="q" @click="send(q)">{{ q }}</button>
      </div>
      <form @submit.prevent="send()">
        <input v-model="input" placeholder="E.g. Suggest a white shirt under 300k" />
        <button class="btn" :disabled="loading">Send</button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { chatApi } from '../services'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const sessionId = ref(localStorage.getItem('fs_chat_session') || '')
const listRef = ref(null)
const messages = ref([
  {
    role: 'assistant',
    text: 'Xin chào! Mình là stylist AI của LUMIA. Bạn cần tư vấn trang phục gì hôm nay?',
  },
])
const quickQuestions = [
  'Gợi ý áo sơ mi trắng',
  'Chính sách đổi trả?',
  'Mã giảm giá hiện có?',
]

async function send(preset) {
  const text = (preset || input.value).trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', text })
  input.value = ''
  loading.value = true
  await nextTick()
  listRef.value?.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
  try {
    const { data } = await chatApi.ask({ message: text, session_id: sessionId.value || undefined })
    sessionId.value = data.session_id
    localStorage.setItem('fs_chat_session', data.session_id)
    messages.value.push({
      role: 'assistant',
      text: data.answer,
      products: data.suggested_products || [],
    })
  } catch {
    messages.value.push({
      role: 'assistant',
      text: 'Xin lỗi, chatbot tạm thời gặp sự cố. Vui lòng thử lại sau.',
    })
  } finally {
    loading.value = false
    await nextTick()
    listRef.value?.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.chat-root {
  position: fixed;
  right: 1.2rem;
  bottom: 1.2rem;
  z-index: 40;
}

.chat-toggle {
  border: 0;
  border-radius: 999px;
  padding: 0.9rem 1.2rem;
  background: var(--accent);
  color: white;
  cursor: pointer;
  box-shadow: var(--shadow);
}

.chat-panel {
  position: absolute;
  right: 0;
  bottom: 3.6rem;
  width: min(380px, calc(100vw - 2rem));
  display: grid;
  gap: 0.8rem;
}

.chat-panel h3 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.7rem;
}

.messages {
  max-height: 320px;
  overflow: auto;
  display: grid;
  gap: 0.7rem;
}

.msg {
  padding: 0.75rem 0.9rem;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.7);
}

.msg.user {
  background: var(--accent-soft);
  justify-self: end;
}

.msg p {
  margin: 0;
  white-space: pre-wrap;
}

.suggestions {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.55rem;
}

.suggestion {
  font-size: 0.9rem;
  color: var(--accent);
  font-weight: 600;
}

.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.quick button {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.6);
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  cursor: pointer;
}

form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.5rem;
}

form input {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.75rem 0.9rem;
  background: rgba(255, 255, 255, 0.8);
}
</style>
