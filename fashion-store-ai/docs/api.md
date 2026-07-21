# API Overview

Base URL: `/api/v1`

## Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PATCH /auth/me`

## Catalog
- `GET /categories`
- `GET /products`
- `GET /products/{id}`
- `GET /promotions`

## Cart & orders
- `GET /cart`
- `POST /cart/items`
- `PATCH /cart/items/{product_id}`
- `DELETE /cart`
- `POST /orders`
- `GET /orders`
- `GET /orders/{id}`

## Chat
- `POST /chat`
- `GET /faqs`
- `GET /store-info`

## Admin
- `GET /admin/dashboard`
- `GET /admin/users`
- `GET /admin/products`
- `GET /admin/orders`
- `PATCH /admin/orders/{id}`
- `POST /faqs`, `PATCH /faqs/{id}`, `DELETE /faqs/{id}`
- `PUT /store-info`
- `GET /admin/chat-logs`
- `POST /admin/reindex`

Interactive docs: `/docs`
