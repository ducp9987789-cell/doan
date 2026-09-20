#!/usr/bin/env python3
"""
=============================================================================
                  FASHION STORE AI - SEED DEMO DATA SCRIPT
=============================================================================
Tạo dữ liệu mẫu hoàn chỉnh:
- Admin:  Admin@fashion.vn   / Admin@123
- Khách:  Tenant@fashion.vn  / Tenant@123
- Danh mục, sản phẩm thời trang phong phú, FAQs, khuyến mãi, đơn hàng demo.
- Tự động nạp dữ liệu vector vào ChromaDB cho Chatbot AI.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Thêm thư mục backend và ai-core vào sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "ai-core"))

from app.core.ai_bootstrap import init_ai_core
from app.core.config import get_settings
from app.core.security import hash_password
from app.core.utils import slugify
from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.services.chat_service import ChatService


SEED_CATEGORIES = [
    {"name": "Áo Nam & Nữ", "slug": "ao", "description": "Áo sơ mi công sở, áo thun phong cách, áo polo thanh lịch"},
    {"name": "Quần Thời Trang", "slug": "quan", "description": "Quần jean slim-fit, quần tây âu, quần short năng động"},
    {"name": "Váy & Đầm Nữ", "slug": "vay", "description": "Váy hoa nhí dạo phố, đầm dạ hội, chân váy chữ A"},
    {"name": "Áo Khoác & Blazer", "slug": "ao-khoac", "description": "Blazer phong cách Hàn Quốc, áo khoác denim, áo dù chống gió"},
    {"name": "Giày & Dép", "slug": "giay-dep", "description": "Sneaker trắng thanh lịch, giày lười da bò, sandal quai hậu"},
    {"name": "Phụ Kiện Cao Cấp", "slug": "phu-kien", "description": "Túi xách da, ví cầm tay, thắt lưng da, nón phong cách"},
]

SEED_PRODUCTS = [
    {
        "name": "Áo sơ mi trắng Oxford Premium",
        "description": "Áo sơ mi trắng chất liệu cotton Oxford dệt chéo cao cấp, chống nhăn, thoáng khí, tôn dáng chuẩn công sở thanh lịch.",
        "price": 389000,
        "sale_price": 329000,
        "category_slug": "ao",
        "colors": ["Trắng", "Xanh Pastel"],
        "sizes": ["S", "M", "L", "XL"],
        "tags": ["ao so mi", "oxford", "cong so", "basic", "nam nu"],
        "stock": 65,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800"],
    },
    {
        "name": "Áo thun Cotton Organic Oversize",
        "description": "Áo thun 100% cotton định lượng 250gsm dày dặn, thấm hút mồ hôi tốt, phong cách streetwear hiện đại.",
        "price": 249000,
        "sale_price": 199000,
        "category_slug": "ao",
        "colors": ["Đen", "Trắng", "Xám Khói"],
        "sizes": ["M", "L", "XL", "XXL"],
        "tags": ["ao thun", "streetwear", "oversize", "unisex"],
        "stock": 90,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800"],
    },
    {
        "name": "Áo Polo dệt kim Smart Casual",
        "description": "Áo Polo cổ bẻ sang trọng, chất dệt kim co giãn 4 chiều mềm mại, thích hợp đi làm và gặp gỡ đối tác.",
        "price": 350000,
        "sale_price": 299000,
        "category_slug": "ao",
        "colors": ["Xanh Navy", "Beiges", "Đen"],
        "sizes": ["S", "M", "L", "XL"],
        "tags": ["polo", "cong so", "smart casual"],
        "stock": 45,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1625910513413-562479e083a9?w=800"],
    },
    {
        "name": "Quần Jean Slim-Fit Denim Co Giãn",
        "description": "Quần jean form slim fit ôm vừa vặn, vải denim dệt sợi spandex co giãn linh hoạt, bền màu theo thời gian.",
        "price": 499000,
        "sale_price": 429000,
        "category_slug": "quan",
        "colors": ["Xanh Đậm", "Xanh Nhạt", "Đen Xước"],
        "sizes": ["29", "30", "31", "32", "33"],
        "tags": ["quan jean", "denim", "slim fit"],
        "stock": 50,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1542272454315-7ad9d70457f5?w=800"],
    },
    {
        "name": "Quần Tây Âu Ống Suông Ly Nổi",
        "description": "Quần tây vải tuyết mưa nhập khẩu mềm mịn, xếp ly nổi tinh tế, cạp cao hack dáng cực chuẩn.",
        "price": 420000,
        "sale_price": None,
        "category_slug": "quan",
        "colors": ["Đen", "Xám Tro", "Nâu Mocha"],
        "sizes": ["S", "M", "L", "XL"],
        "tags": ["quan tay", "quan au", "cong so"],
        "stock": 38,
        "is_featured": False,
        "images": ["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800"],
    },
    {
        "name": "Váy Midi Hoa Nhí Vintage",
        "description": "Váy đầm midi hoa nhí phong cách lãng mạn, cổ V tôn cổ thon gọn, eo chiết nhẹ nhàng tôn đường cong.",
        "price": 389000,
        "sale_price": 329000,
        "category_slug": "vay",
        "colors": ["Hồng Pastel", "Xanh Mint", "Vàng Nhạt"],
        "sizes": ["S", "M", "L"],
        "tags": ["vay", "hoa nhi", "vintage", "dao pho"],
        "stock": 30,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800"],
    },
    {
        "name": "Đầm Dự Tiệc Bodycon Sang Trọng",
        "description": "Đầm dạ hội ôm body xẻ tà thanh thoát, chất liệu nhung satin óng ánh quyến rũ cho các buổi tiệc tối.",
        "price": 650000,
        "sale_price": 549000,
        "category_slug": "vay",
        "colors": ["Đỏ Rượu", "Đen Huyền Bí"],
        "sizes": ["S", "M", "L"],
        "tags": ["dam tiec", "bodycon", "sang trong"],
        "stock": 25,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800"],
    },
    {
        "name": "Áo Blazer Phong Cách Hàn Quốc",
        "description": "Blazer 2 hàng khuy form suông hiện đại, lót lụa cao cấp 2 lớp, chuẩn phong cách thanh lịch Seoul.",
        "price": 690000,
        "sale_price": 599000,
        "category_slug": "ao-khoac",
        "colors": ["Be", "Đen", "Kẻ Caro"],
        "sizes": ["S", "M", "L"],
        "tags": ["blazer", "ao khoac", "han quoc", "cong so"],
        "stock": 35,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800"],
    },
    {
        "name": "Áo Khoác Denim Jacket Retro",
        "description": "Áo khoác bò phong cách cổ điển, chất jean 14oz dày dặn, nút kim loại khắc laser sắc nét.",
        "price": 520000,
        "sale_price": 459000,
        "category_slug": "ao-khoac",
        "colors": ["Xanh Vintage", "Xám Khói"],
        "sizes": ["M", "L", "XL"],
        "tags": ["ao khoac", "denim", "jean", "retro"],
        "stock": 40,
        "is_featured": False,
        "images": ["https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800"],
    },
    {
        "name": "Giày Sneaker Da Trắng Minimalist",
        "description": "Sneaker da bò tổng hợp êm ái, đế cao su nguyên khối chống trơn trượt, dễ dàng phối mọi trang phục.",
        "price": 590000,
        "sale_price": 499000,
        "category_slug": "giay-dep",
        "colors": ["Trắng Full", "Trắng Gót Đen"],
        "sizes": ["38", "39", "40", "41", "42", "43"],
        "tags": ["giay", "sneaker", "minimalist", "trang"],
        "stock": 60,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800"],
    },
    {
        "name": "Túi Xách Da Đeo Chéo Minimalist",
        "description": "Túi da PU cao cấp chống thấm nước, khoá kéo kim loại trơn tru, nhiều ngăn tiện lợi chứa iPad và sổ tay.",
        "price": 380000,
        "sale_price": 299000,
        "category_slug": "phu-kien",
        "colors": ["Đen", "Nâu Bò", "Be"],
        "sizes": ["One size"],
        "tags": ["tui xach", "da", "phu kien", "deo cheo"],
        "stock": 55,
        "is_featured": True,
        "images": ["https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800"],
    },
    {
        "name": "Thắt Lưng Da Bò Khóa Tự Động",
        "description": "Dây nịt da bò nguyên miếng mềm mại, mặt khoá hợp kim phủ titan chống trầy, tinh tế đẳng cấp.",
        "price": 280000,
        "sale_price": 219000,
        "category_slug": "phu-kien",
        "colors": ["Đen", "Nâu Đậm"],
        "sizes": ["110cm", "120cm"],
        "tags": ["that lung", "da bo", "phu kien nam"],
        "stock": 70,
        "is_featured": False,
        "images": ["https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=800"],
    },
]

SEED_FAQS = [
    {
        "question": "Thời gian giao hàng của shop mất bao lâu?",
        "answer": "Khu vực nội thành Hà Nội & TP.HCM nhận hàng trong 1-2 ngày. Các tỉnh thành khác từ 2-4 ngày làm việc. Bạn sẽ nhận được mã vận đơn theo dõi đơn hàng sau khi xác nhận.",
        "category": "shipping",
    },
    {
        "question": "Chính sách đổi trả sản phẩm như thế nào?",
        "answer": "Shop hỗ trợ đổi trả miễn phí trong vòng 7 ngày kể từ khi nhận hàng nếu sản phẩm lỗi từ nhà sản xuất, không vừa size hoặc không đúng mẫu mã (yêu cầu còn nguyên tem mác).",
        "category": "return",
    },
    {
        "question": "Làm sao để chọn đúng size áo và quần?",
        "answer": "Bạn có thể gửi chiều cao, cân nặng và form dáng mong muốn cho chatbot AI để được tư vấn chính xác nhất hoặc tham khảo bảng số đo chi tiết trong trang chi tiết sản phẩm.",
        "category": "sizing",
    },
    {
        "question": "Shop có những hình thức thanh toán nào?",
        "answer": "Chúng tôi hỗ trợ: Thanh toán khi nhận hàng (COD), Chuyển khoản ngân hàng trực tiếp, và các ví điện tử phổ biến.",
        "category": "payment",
    },
    {
        "question": "Tôi có được kiểm tra hàng trước khi thanh toán không?",
        "answer": "Có. Khách hàng luôn được quyền đồng kiểm tra ngoại quan sản phẩm trước khi thanh toán cho nhân viên giao hàng.",
        "category": "shipping",
    },
    {
        "question": "Hướng dẫn bảo quản quần áo thời trang đúng cách?",
        "answer": "Nên giặt ở nhiệt độ thường, phân loại đồ sáng/tối màu, tránh dùng chất tẩy mạnh và phơi trong bóng râm thoáng gió để giữ màu sắc bền lâu.",
        "category": "general",
    },
]

SEED_PROMOTIONS = [
    {
        "code": "WELCOME10",
        "title": "Giảm 10% cho khách hàng mới",
        "description": "Áp dụng cho mọi đơn hàng đầu tiên từ 300.000đ",
        "discount_type": "percent",
        "discount_value": 10,
        "min_order_value": 300000,
        "is_active": True,
    },
    {
        "code": "FREESHIP",
        "title": "Miễn phí vận chuyển 30.000đ",
        "description": "Giảm trực tiếp 30.000đ phí giao hàng cho đơn từ 200.000đ",
        "discount_type": "fixed",
        "discount_value": 30000,
        "min_order_value": 200000,
        "is_active": True,
    },
    {
        "code": "FASHION2026",
        "title": "Voucher Fashion Store 2026",
        "description": "Giảm ngay 50.000đ cho đơn hàng giá trị từ 500.000đ",
        "discount_type": "fixed",
        "discount_value": 50000,
        "min_order_value": 500000,
        "is_active": True,
    },
    {
        "code": "VIP50",
        "title": "Ưu đãi tri ân thành viên VIP",
        "description": "Giảm 15% tối đa 150.000đ cho khách hàng thân thiết",
        "discount_type": "percent",
        "discount_value": 15,
        "min_order_value": 600000,
        "is_active": True,
    },
]


async def run_seed(reset_db: bool = False):
    print("\n" + "=" * 60)
    print("🚀 BẮT ĐẦU KHỞI TẠO DỮ LIỆU DEMO CHO FASHION STORE AI")
    print("=" * 60)

    # 1. Kết nối MongoDB & AI-Core
    await connect_to_mongo()
    db = get_database()
    await init_ai_core()

    if reset_db:
        print("\n⚠️  Đang xóa dữ liệu cũ theo yêu cầu (--reset)...")
        await db.users.delete_many({})
        await db.categories.delete_many({})
        await db.products.delete_many({})
        await db.faqs.delete_many({})
        await db.promotions.delete_many({})
        await db.store_info.delete_many({})
        await db.orders.delete_many({})
        print("✅ Đã làm sạch toàn bộ collections trong MongoDB.")

    # 2. Tạo tài khoản Admin & Tenant
    print("\n👤 Khởi tạo tài khoản hệ thống:")
    
    # Admin
    admin_email = "admin@fashion.vn"
    admin_user = await db.users.find_one({"email": admin_email})
    if not admin_user:
        await db.users.insert_one(
            {
                "email": admin_email,
                "full_name": "Quản Trị Viên Fashion Store",
                "hashed_password": hash_password("Admin@123"),
                "role": "admin",
                "phone": "0988888888",
                "address": "12 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP.HCM",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        print(f"  [+] Tạo mới Admin:   {admin_email} / Admin@123 (Role: admin)")
    else:
        await db.users.update_one(
            {"_id": admin_user["_id"]},
            {"$set": {"hashed_password": hash_password("Admin@123"), "role": "admin", "is_active": True}}
        )
        print(f"  [*] Cập nhật Admin:  {admin_email} / Admin@123 (Role: admin)")

    # Tenant / Customer
    tenant_email = "tenant@fashion.vn"
    tenant_user = await db.users.find_one({"email": tenant_email})
    tenant_id = None
    if not tenant_user:
        res = await db.users.insert_one(
            {
                "email": tenant_email,
                "full_name": "Nguyễn Văn Tenant (Khách Hàng VIP)",
                "hashed_password": hash_password("Tenant@123"),
                "role": "customer",
                "phone": "0912345678",
                "address": "88 Nam Kỳ Khởi Nghĩa, Quận 3, TP.HCM",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        tenant_id = str(res.inserted_id)
        print(f"  [+] Tạo mới Khách:   {tenant_email} / Tenant@123 (Role: customer)")
    else:
        tenant_id = str(tenant_user["_id"])
        await db.users.update_one(
            {"_id": tenant_user["_id"]},
            {"$set": {"hashed_password": hash_password("Tenant@123"), "role": "customer", "is_active": True}}
        )
        print(f"  [*] Cập nhật Khách:  {tenant_email} / Tenant@123 (Role: customer)")

    # 3. Tạo Danh mục (Categories)
    print("\n📂 Khởi tạo danh mục sản phẩm:")
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many(
            [
                {
                    **cat,
                    "image_url": "",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
                for cat in SEED_CATEGORIES
            ]
        )
        print(f"  [+] Đã thêm {len(SEED_CATEGORIES)} danh mục thời trang.")
    else:
        print(f"  [*] Danh mục đã tồn tại ({await db.categories.count_documents({})} danh mục).")

    categories_list = await db.categories.find({}).to_list(length=100)
    category_map = {doc["slug"]: str(doc["_id"]) for doc in categories_list}
    category_name_map = {doc["slug"]: doc["name"] for doc in categories_list}

    # 4. Tạo Sản phẩm (Products)
    print("\n👗 Khởi tạo sản phẩm thời trang:")
    if await db.products.count_documents({}) == 0:
        product_docs = []
        for item in SEED_PRODUCTS:
            category_slug = item["category_slug"]
            cat_id = category_map.get(category_slug, "")
            cat_name = category_name_map.get(category_slug, "")
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
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "variants": [
                        {"color": color, "size": size, "stock": max(item["stock"] // max(len(item["colors"]) * len(item["sizes"]), 1), 2)}
                        for color in item["colors"]
                        for size in item["sizes"]
                    ],
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )
        await db.products.insert_many(product_docs)
        print(f"  [+] Đã thêm {len(SEED_PRODUCTS)} sản phẩm thời trang chất lượng cao.")
    else:
        print(f"  [*] Sản phẩm đã tồn tại ({await db.products.count_documents({})} sản phẩm).")

    # 5. FAQs
    print("\n❓ Khởi tạo FAQs:")
    if await db.faqs.count_documents({}) == 0:
        await db.faqs.insert_many(
            [{**faq, "is_active": True, "created_at": datetime.utcnow()} for faq in SEED_FAQS]
        )
        print(f"  [+] Đã thêm {len(SEED_FAQS)} câu hỏi thường gặp.")
    else:
        print(f"  [*] FAQs đã tồn tại ({await db.faqs.count_documents({})} câu).")

    # 6. Khuyến mãi (Promotions)
    print("\n🎁 Khởi tạo mã khuyến mãi:")
    if await db.promotions.count_documents({}) == 0:
        await db.promotions.insert_many(
            [{**promo, "created_at": datetime.utcnow()} for promo in SEED_PROMOTIONS]
        )
        print(f"  [+] Đã thêm {len(SEED_PROMOTIONS)} mã voucher.")
    else:
        print(f"  [*] Khuyến mãi đã tồn tại ({await db.promotions.count_documents({})} mã).")

    # 7. Thông tin cửa hàng (Store Info)
    print("\n🏪 Khởi tạo thông tin cửa hàng:")
    if await db.store_info.count_documents({}) == 0:
        await db.store_info.insert_one(
            {
                "store_name": "Fashion Store AI",
                "hotline": "1900 6868 (8:00 - 22:00)",
                "email": "support@fashionstore.local",
                "address": "12 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
                "shipping_policy": "Miễn phí giao hàng toàn quốc với đơn từ 500.000đ. Thời gian giao từ 1 - 3 ngày làm việc.",
                "return_policy": "Đổi trả tận nơi miễn phí trong 7 ngày đối với sản phẩm còn nguyên tem mác.",
                "about": "Fashion Store AI - Nền tảng thời trang thông minh tích hợp trợ lý AI Shopping Assistant tư vấn phong cách & sản phẩm 24/7.",
                "updated_at": datetime.utcnow(),
            }
        )
        print("  [+] Đã lưu thông tin cửa hàng và chính sách bán hàng.")
    else:
        print("  [*] Thông tin cửa hàng đã có.")

    # 8. Đơn hàng mẫu cho khách hàng
    print("\n📦 Khởi tạo đơn hàng demo cho khách hàng Tenant:")
    if tenant_id and await db.orders.count_documents({"user_id": tenant_id}) == 0:
        products_list = await db.products.find({}).to_list(length=5)
        if len(products_list) >= 2:
            p1 = products_list[0]
            p2 = products_list[1]
            orders_demo = [
                {
                    "user_id": tenant_id,
                    "items": [
                        {
                            "product_id": str(p1["_id"]),
                            "name": p1["name"],
                            "price": p1.get("sale_price") or p1["price"],
                            "quantity": 1,
                            "color": p1["colors"][0] if p1.get("colors") else "Mặc định",
                            "size": p1["sizes"][0] if p1.get("sizes") else "M",
                            "image": p1["images"][0] if p1.get("images") else "",
                        },
                        {
                            "product_id": str(p2["_id"]),
                            "name": p2["name"],
                            "price": p2.get("sale_price") or p2["price"],
                            "quantity": 2,
                            "color": p2["colors"][0] if p2.get("colors") else "Mặc định",
                            "size": p2["sizes"][0] if p2.get("sizes") else "L",
                            "image": p2["images"][0] if p2.get("images") else "",
                        },
                    ],
                    "shipping_address": {
                        "full_name": "Nguyễn Văn Tenant",
                        "phone": "0912345678",
                        "address": "88 Nam Kỳ Khởi Nghĩa",
                        "city": "TP. Hồ Chí Minh",
                        "district": "Quận 3",
                        "note": "Giao giờ hành chính, gọi trước khi đến",
                    },
                    "payment_method": "cod",
                    "status": "delivered",
                    "subtotal": (p1.get("sale_price") or p1["price"]) + 2 * (p2.get("sale_price") or p2["price"]),
                    "discount": 30000,
                    "shipping_fee": 0,
                    "total": (p1.get("sale_price") or p1["price"]) + 2 * (p2.get("sale_price") or p2["price"]) - 30000,
                    "promotion_code": "FREESHIP",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                {
                    "user_id": tenant_id,
                    "items": [
                        {
                            "product_id": str(p1["_id"]),
                            "name": p1["name"],
                            "price": p1.get("sale_price") or p1["price"],
                            "quantity": 1,
                            "color": p1["colors"][0] if p1.get("colors") else "Mặc định",
                            "size": p1["sizes"][1] if len(p1.get("sizes", [])) > 1 else "L",
                            "image": p1["images"][0] if p1.get("images") else "",
                        }
                    ],
                    "shipping_address": {
                        "full_name": "Nguyễn Văn Tenant",
                        "phone": "0912345678",
                        "address": "88 Nam Kỳ Khởi Nghĩa",
                        "city": "TP. Hồ Chí Minh",
                        "district": "Quận 3",
                        "note": "Giao nhanh trong hôm nay",
                    },
                    "payment_method": "bank_transfer",
                    "status": "shipping",
                    "subtotal": (p1.get("sale_price") or p1["price"]),
                    "discount": 0,
                    "shipping_fee": 30000,
                    "total": (p1.get("sale_price") or p1["price"]) + 30000,
                    "promotion_code": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            ]
            await db.orders.insert_many(orders_demo)
            print(f"  [+] Đã tạo 2 đơn hàng mẫu cho tài khoản {tenant_email}.")
    else:
        print(f"  [*] Đơn hàng cho {tenant_email} đã tồn tại.")

    # 9. Reindex Vector Store cho AI Chatbot
    print("\n🧠 Nạp dữ liệu Vector Store ChromaDB cho Chatbot AI:")
    try:
        indexed_count = await ChatService.reindex_knowledge()
        print(f"  [+] Đã đánh chỉ mục {indexed_count} tài liệu kiến thức vào ChromaDB.")
    except Exception as e:
        print(f"  [!] Lưu ý: Reindex ChromaDB ({e})")

    # Đóng kết nối
    await close_mongo_connection()

    # Tổng kết
    print("\n" + "=" * 60)
    print("✨ HOÀN THÀNH KHỞI TẠO DỮ LIỆU DEMO THÀNH CÔNG!")
    print("=" * 60)
    print("📋 THÔNG TIN TÀI KHOẢN ĐĂNG NHẬP:")
    print("  👑 QUẢN TRỊ VIÊN (Admin):")
    print("     - Email:    Admin@fashion.vn")
    print("     - Mật khẩu: Admin@123")
    print("     - Quyền:    Xem Dashboard, quản lý sản phẩm, đơn hàng, chatbot")
    print("")
    print("  🛍️  KHÁCH HÀNG (Customer):")
    print("     - Email:    Tenant@fashion.vn")
    print("     - Mật khẩu: Tenant@123")
    print("     - Quyền:    Mua sắm, giỏ hàng, xem 2 đơn hàng demo, chat AI")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Seed demo data for Fashion Store AI")
    parser.add_argument("--reset", action="store_true", help="Xóa sạch dữ liệu cũ và khởi tạo lại từ đầu")
    args = parser.parse_args()

    asyncio.run(run_seed(reset_db=args.reset))


if __name__ == "__main__":
    main()
