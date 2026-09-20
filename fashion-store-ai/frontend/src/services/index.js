import api from './api'

export const authApi = {
  register: (payload) => api.post('/auth/register', payload),
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/auth/me'),
}

export const productApi = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  categories: (params) => api.get('/categories', { params }),
  createCategory: (payload) => api.post('/categories', payload),
  updateCategory: (id, payload) => api.patch(`/categories/${id}`, payload),
  deleteCategory: (id) => api.delete(`/categories/${id}`),

  promotions: (params) => api.get('/promotions', { params }),
  createPromotion: (payload) => api.post('/promotions', payload),
  updatePromotion: (id, payload) => api.patch(`/promotions/${id}`, payload),
  deletePromotion: (id) => api.delete(`/promotions/${id}`),

  create: (payload) => api.post('/products', payload),
  update: (id, payload) => api.patch(`/products/${id}`, payload),
  remove: (id) => api.delete(`/products/${id}`),
}

export const orderApi = {
  getCart: () => api.get('/cart'),
  addToCart: (payload) => api.post('/cart/items', payload),
  updateCartItem: (productId, payload, params) =>
    api.patch(`/cart/items/${productId}`, payload, { params }),
  clearCart: () => api.delete('/cart'),
  createOrder: (payload) => api.post('/orders', payload),
  myOrders: () => api.get('/orders'),
  getOrder: (id) => api.get(`/orders/${id}`),
  adminOrders: () => api.get('/admin/orders'),
  updateOrderStatus: (id, status) => api.patch(`/admin/orders/${id}`, { status }),
}

export const chatApi = {
  ask: (payload) => api.post('/chat', payload),
  faqs: () => api.get('/faqs'),
  createFaq: (payload) => api.post('/faqs', payload),
  updateFaq: (id, payload) => api.patch(`/faqs/${id}`, payload),
  deleteFaq: (id) => api.delete(`/faqs/${id}`),

  storeInfo: () => api.get('/store-info'),
  updateStoreInfo: (payload) => api.put('/store-info', payload),

  chatLogs: () => api.get('/admin/chat-logs'),
  reindex: () => api.post('/admin/reindex'),
}

export const adminApi = {
  dashboard: () => api.get('/admin/dashboard'),
  users: () => api.get('/admin/users'),
  products: (params) => api.get('/admin/products', { params }),
}
