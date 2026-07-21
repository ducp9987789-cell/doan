from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.core.security import hash_password
from app.core.utils import slugify
from app.db.mongodb import get_database
from app.services.chat_service import ChatService


SEED_CATEGORIES = [
    {"name": "Áo", "slug": "ao", "description": "Áo sơ mi, áo thun, áo khoác"},
    {"name": "Quần", "slug": "quan", "description": "Quần jean, quần tây, quần short"},
    {"name": "Váy", "slug": "vay", "description": "Váy công sở và dạo phố"},
    {"name": "Phụ kiện", "slug": "phu-kien", "description": "Túi, thắt lưng, mũ"},
]

SEED_PRODUCTS = [
    {
        "name": "Áo sơ mi trắng basic",
        "description": "Áo sơ mi trắng form regular, chất liệu cotton dễ phối đồ công sở và thường ngày.",
        "price": 299000,
        "sale_price": 249000,
        "category_slug": "ao",
        "colors": ["Trắng", "Xanh nhạt"],
        "sizes": ["S", "M", "L", "XL"],
        "tags": ["ao so mi", "cong so", "basic"],
        "stock": 40,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800"],
    },
    {
        "name": "Áo thun overlay đen",
        "description": "Áo thun cotton 100% màu đen, form oversized trẻ trung.",
        "price": 199000,
        "sale_price": None,
        "category_slug": "ao",
        "colors": ["Đen", "Xám"],
        "sizes": ["M", "L", "XL"],
        "tags": ["ao thun", "casual", "streetwear"],
        "stock": 55,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800"],
    },
    {
        "name": "Quần jean slim xanh",
        "description": "Quần jean slim-fit co giãn nhẹ, phù hợp đi làm và đi chơi.",
        "price": 459000,
        "sale_price": 399000,
        "category_slug": "quan",
        "colors": ["Xanh đậm", "Xanh nhạt"],
        "sizes": ["28", "29", "30", "31", "32"],
        "tags": ["jean", "slim", "denim"],
        "stock": 35,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1542272454315-7ad9d70457f5?w=800"],
    },
    {
        "name": "Quần tây ống đứng",
        "description": "Quần tây công sở ống đứng, chất liệu thoáng mát.",
        "price": 389000,
        "sale_price": None,
        "category_slug": "quan",
        "colors": ["Đen", "Be", "Xám"],
        "sizes": ["S", "M", "L"],
        "tags": ["quan tay", "cong so"],
        "stock": 28,
        "is_featured": False,
        "images": ["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800"],
    },
    {
        "name": "Váy midi hoa nhí",
        "description": "Váy midi họa tiết hoa nhí, eo chun linh hoạt, phù hợp dạo phố.",
        "price": 349000,
        "sale_price": 299000,
        "category_slug": "vay",
        "colors": ["Hồng", "Xanh mint"],
        "sizes": ["S", "M", "L"],
        "tags": ["vay", "hoa nhi", "nu"],
        "stock": 22,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800"],
    },
    {
        "name": "Túi đeo chéo canvas",
        "description": "Túi canvas tối giản, ngăn rộng, phù hợp đi học đi làm.",
        "price": 259000,
        "sale_price": None,
        "category_slug": "phu-kien",
        "colors": ["Be", "Đen"],
        "sizes": ["One size"],
        "tags": ["tui", "canvas", "phu kien"],
        "stock": 45,
        "is_featured": False,
        "images": ["https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800"],
    },
]

SEED_FAQS = [
    {
        "question": "Shop giao hàng trong bao lâu?",
        "answer": "Nội thành 1-2 ngày, ngoại tỉnh 2-4 ngày làm việc kể từ khi xác nhận đơn.",
        "category": "shipping",
    },
    {
        "question": "Chính sách đổi trả như thế nào?",
        "answer": "Đổi trả trong 7 ngày nếu sản phẩm còn nguyên tem mác, chưa qua sử dụng.",
        "category": "return",
    },
    {
        "question": "Có hỗ trợ tư vấn size không?",
        "answer": "Có. Bạn cho chatbot biết chiều cao, cân nặng và phong cách mong muốn để được gợi ý.",
        "category": "sizing",
    },
    {
        "question": "Phương thức thanh toán nào được hỗ trợ?",
        "answer": "Hiện hỗ trợ COD và chuyển khoản ngân hàng khi xác nhận đơn.",
        "category": "payment",
    },
]

SEED_PROMOTIONS = [
    {
        "code": "WELCOME10",
        "title": "Giảm 10% cho khách mới",
        "description": "Áp dụng cho đơn từ 300.000đ",
        "discount_type": "percent",
        "discount_value": 10,
        "min_order_value": 300000,
        "is_active": True,
    },
    {
        "code": "FREESHIP",
        "title": "Giảm phí ship 30.000đ",
        "description": "Giảm cố định 30.000đ cho đơn từ 200.000đ",
        "discount_type": "fixed",
        "discount_value": 30000,
        "min_order_value": 200000,
        "is_active": True,
    },
]


async def seed_database() -> dict[str, Any]:
    settings = get_settings()
    db = get_database()

    if await db.users.count_documents({}) == 0:
        await db.users.insert_many(
            [
                {
                    "email": settings.admin_email,
                    "full_name": "Store Admin",
                    "hashed_password": hash_password(settings.admin_password),
                    "role": "admin",
                    "phone": "0900000000",
                    "address": "Quận 1, TP.HCM",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                {
                    "email": "customer@fashionstore.local",
                    "full_name": "Demo Customer",
                    "hashed_password": hash_password("Customer@123"),
                    "role": "customer",
                    "phone": "0911111111",
                    "address": "Quận 3, TP.HCM",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            ]
        )

    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many(
            [
                {
                    **category,
                    "image_url": "",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
                for category in SEED_CATEGORIES
            ]
        )

    category_map = {
        doc["slug"]: str(doc["_id"])
        for doc in await db.categories.find({}).to_list(length=100)
    }
    category_name_map = {
        doc["slug"]: doc["name"]
        for doc in await db.categories.find({}).to_list(length=100)
    }

    if await db.products.count_documents({}) == 0:
        product_docs = []
        for item in SEED_PRODUCTS:
            category_slug = item["category_slug"]
            product_docs.append(
                {
                    "name": item["name"],
                    "description": item["description"],
                    "price": item["price"],
                    "sale_price": item["sale_price"],
                    "colors": item["colors"],
                    "sizes": item["sizes"],
                    "tags": item["tags"],
                    "stock": item["stock"],
                    "is_featured": item["is_featured"],
                    "images": item["images"],
                    "slug": slugify(item["name"]),
                    "category_id": category_map[category_slug],
                    "category_name": category_name_map[category_slug],
                    "variants": [
                        {"color": color, "size": size, "stock": max(item["stock"] // 4, 1)}
                        for color in item["colors"]
                        for size in item["sizes"]
                    ],
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )
        await db.products.insert_many(product_docs)

    if await db.faqs.count_documents({}) == 0:
        await db.faqs.insert_many(
            [{**faq, "is_active": True, "created_at": datetime.utcnow()} for faq in SEED_FAQS]
        )

    if await db.promotions.count_documents({}) == 0:
        await db.promotions.insert_many(
            [{**promo, "created_at": datetime.utcnow()} for promo in SEED_PROMOTIONS]
        )

    if await db.store_info.count_documents({}) == 0:
        await db.store_info.insert_one(
            {
                "store_name": "Fashion Store AI",
                "hotline": "1900 6868",
                "email": "support@fashionstore.local",
                "address": "12 Nguyễn Huệ, Quận 1, TP.HCM",
                "shipping_policy": "Miễn phí ship đơn từ 500.000đ. Nội thành 1-2 ngày, ngoại tỉnh 2-4 ngày.",
                "return_policy": "Đổi trả trong 7 ngày với sản phẩm còn tem mác, chưa sử dụng.",
                "about": "Cửa hàng thời trang trực tuyến tích hợp chatbot AI hỗ trợ tư vấn và bán hàng 24/7.",
                "updated_at": datetime.utcnow(),
            }
        )

    indexed = await ChatService.reindex_knowledge()
    return {
        "users": await db.users.count_documents({}),
        "categories": await db.categories.count_documents({}),
        "products": await db.products.count_documents({}),
        "faqs": await db.faqs.count_documents({}),
        "promotions": await db.promotions.count_documents({}),
        "indexed_documents": indexed,
    }
