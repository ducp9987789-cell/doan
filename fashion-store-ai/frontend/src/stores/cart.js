import { defineStore } from 'pinia'
import { orderApi } from '../services'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    subtotal: 0,
    itemCount: 0,
    loading: false,
  }),
  actions: {
    async fetchCart() {
      this.loading = true
      try {
        const { data } = await orderApi.getCart()
        this.items = data.items
        this.subtotal = data.subtotal
        this.itemCount = data.item_count
      } finally {
        this.loading = false
      }
    },
    async addItem(payload) {
      const { data } = await orderApi.addToCart(payload)
      this.items = data.items
      this.subtotal = data.subtotal
      this.itemCount = data.item_count
    },
    async updateItem(productId, quantity, color, size) {
      const { data } = await orderApi.updateCartItem(productId, { quantity }, { color, size })
      this.items = data.items
      this.subtotal = data.subtotal
      this.itemCount = data.item_count
    },
    reset() {
      this.items = []
      this.subtotal = 0
      this.itemCount = 0
    },
  },
})
