# Requirements

## Customer
- Register and login with JWT
- Browse and filter products by category, color, size, price, keyword
- View product detail and add to cart
- Checkout with shipping info and promotion code
- Track personal orders
- Chat with AI assistant

## Admin
- Dashboard metrics
- Manage categories and products
- Manage order statuses
- Manage promotions
- Manage FAQ and store policies
- Reindex chatbot knowledge into Qdrant
- Persist chat sessions in Redis
- Cache RAG retrieval results in Redis

## Chatbot
- Answer product and policy questions with RAG
- Suggest related products
- Persist chat logs
