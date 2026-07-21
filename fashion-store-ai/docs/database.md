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

## Chatbot knowledge sources

Indexed into Chroma collection `fashion_knowledge`:

- active products
- FAQ
- promotions
- store shipping/return policies
