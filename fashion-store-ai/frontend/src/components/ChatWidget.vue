<template>
  <div class="chat-root">
    <!-- Nút mở Chatbot AI Stylist ở góc phải màn hình -->
    <button class="chat-toggle" @click="open = !open" title="Trò chuyện cùng AI Stylist">
      <div class="toggle-icon">
        <svg v-if="!open" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </div>
      <span class="toggle-text">{{ open ? 'Đóng chat' : 'AI Stylist' }}</span>
      <span v-if="!open" class="online-dot"></span>
    </button>

    <!-- Hộp thoại chat -->
    <section v-if="open" class="chat-panel panel fade-up">
      <header class="chat-header">
        <div class="ai-avatar">AI</div>
        <div class="header-info">
          <h3>Fashion AI Stylist</h3>
          <p class="muted">Tư vấn chọn đồ, phối outfit & giải đáp 24/7</p>
        </div>
      </header>

      <!-- Danh sách tin nhắn -->
      <div class="messages-container" ref="listRef">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="chat-msg"
          :class="msg.role"
        >
          <p class="msg-text">{{ msg.text }}</p>

          <!-- Danh sách sản phẩm được AI đề xuất -->
          <div v-if="msg.products?.length" class="suggested-products">
            <span class="sugg-title">🛍️ Sản phẩm gợi ý:</span>
            <RouterLink
              v-for="product in msg.products"
              :key="product.id"
              :to="`/products/${product.id}`"
              class="sugg-item"
              @click="open = false"
            >
              <span>{{ product.name }}</span>
              <small>{{ formatPrice(product.sale_price || product.price) }}</small>
            </RouterLink>
          </div>
        </div>

        <div v-if="loading" class="chat-msg assistant typing">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <!-- Câu hỏi nhanh gợi ý -->
      <div class="quick-questions">
        <span class="quick-title">Gợi ý câu hỏi:</span>
        <div class="quick-chips">
          <button
            v-for="q in quickQuestions"
            :key="q"
            class="chip-btn"
            type="button"
            @click="send(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <!-- Form nhập câu hỏi -->
      <form class="chat-input-form" @submit.prevent="send()">
        <input
          v-model="input"
          class="chat-input"
          placeholder="Hỏi AI về phối đồ, chọn size, voucher..."
        />
        <button class="btn btn-send" :disabled="loading" title="Gửi câu hỏi">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
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
    text: 'Xin chào! Mình là Stylist AI của Fashion Store. Bạn cần tư vấn phối trang phục, chọn size hay hỏi thông tin khuyến mãi gì hôm nay?',
  },
])

const quickQuestions = [
  'Gợi ý áo sơ mi công sở',
  'Chính sách đổi trả hàng?',
  'Mã giảm giá đang có?',
  'Tư vấn chọn size theo chiều cao',
]

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

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
      text: 'Xin lỗi bạn, trợ lý AI tạm thời gặp gián đoạn kết nối. Vui lòng thử lại sau giây lát nhé!',
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
  right: 1.5rem;
  bottom: 1.5rem;
  z-index: 1000;
}

.chat-toggle {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border: 0;
  border-radius: 999px;
  padding: 0.85rem 1.4rem;
  background: var(--accent);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(17, 75, 67, 0.35);
  transition: all 0.25s ease;
  position: relative;
}

.chat-toggle:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(17, 75, 67, 0.45);
}

.online-dot {
  width: 9px;
  height: 9px;
  background: #4caf50;
  border: 2px solid #ffffff;
  border-radius: 50%;
  position: absolute;
  top: 8px;
  right: 12px;
}

.chat-panel {
  position: absolute;
  right: 0;
  bottom: 4.2rem;
  width: min(420px, calc(100vw - 2rem));
  background: #ffffff;
  border-radius: 20px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--line);
  padding: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1.2rem;
  background: var(--accent);
  color: #ffffff;
}

.ai-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--accent-gold);
  color: #171411;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.header-info h3 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.3rem;
  color: #ffffff;
  line-height: 1.1;
}

.header-info p {
  margin: 0.15rem 0 0;
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.85);
}

.messages-container {
  max-height: 340px;
  min-height: 220px;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background: #faf8f5;
}

.chat-msg {
  max-width: 86%;
  padding: 0.75rem 1rem;
  border-radius: 14px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.chat-msg.user {
  background: var(--accent);
  color: #ffffff;
  align-self: flex-end;
  border-bottom-right-radius: 3px;
}

.chat-msg.assistant {
  background: #ffffff;
  color: var(--ink);
  align-self: flex-start;
  border: 1px solid var(--line);
  border-bottom-left-radius: 3px;
  box-shadow: var(--shadow-sm);
}

.msg-text {
  margin: 0;
  white-space: pre-wrap;
}

.suggested-products {
  margin-top: 0.8rem;
  padding-top: 0.6rem;
  border-top: 1px dashed var(--line);
  display: grid;
  gap: 0.4rem;
}

.sugg-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--accent);
}

.sugg-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg);
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 0.82rem;
  color: var(--ink);
  transition: background 0.2s ease;
}

.sugg-item:hover {
  background: var(--accent-light);
  color: var(--accent);
}

.sugg-item small {
  font-weight: 700;
  color: var(--accent);
}

.quick-questions {
  padding: 0.6rem 1rem;
  background: #ffffff;
  border-top: 1px solid var(--line);
}

.quick-title {
  display: block;
  font-size: 0.72rem;
  color: var(--muted);
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
}

.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.chip-btn {
  border: 1px solid var(--line-strong);
  background: #ffffff;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent);
}

.chat-input-form {
  display: flex;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  background: #ffffff;
  border-top: 1px solid var(--line);
}

.chat-input {
  flex: 1;
  border: 1.5px solid var(--line-strong);
  border-radius: 999px;
  padding: 0.6rem 1rem;
  font-size: 0.88rem;
  outline: none;
  background: var(--bg);
}

.chat-input:focus {
  border-color: var(--accent);
  background: #ffffff;
}

.btn-send {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Typing animation */
.typing {
  display: flex;
  gap: 4px;
  padding: 0.9rem 1.2rem;
}

.dot {
  width: 6px;
  height: 6px;
  background: var(--muted);
  border-radius: 50%;
  animation: typingBounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
