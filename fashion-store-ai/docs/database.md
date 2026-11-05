# Database

## MongoDB collections

- `users`
- `categories`
- `products`
- `carts`
- `orders`
- `promotions`
- `faqs`
- `store_info`
- `chat_logs`

## Product fields

- name, slug, description
- price, sale_price
- category_id, category_name
- images, colors, sizes, variants
- tags, stock, is_featured, is_active

## Chatbot knowledge sources (RAG)

Indexed into Qdrant collection `fashion_knowledge`:

- active products
- FAQ
- promotions
- store shipping/return policies

## Redis

- `chat:session:{session_id}` — conversation turns for the shopping agent (TTL)
- `rag:cache:{hash}` — short-lived RAG retrieval cache (invalidated on reindex)
