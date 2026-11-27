from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Các thư mục chứa file prompt text
PROMPT_DIRS = [
    Path(__file__).resolve().parent,  # backend/ai-core/prompts
    Path(__file__).resolve().parent.parent.parent / "app" / "services",  # backend/app/services
    Path("/app/ai-core/prompts"),  # Docker container paths
    Path("/app/app/services"),
]


class ComplexityMode(str, Enum):
    """Độ phức tạp tin nhắn: SIMPLE bỏ qua tool; COMPLEX mới chọn RAG/MCP."""

    SIMPLE = "simple"
    COMPLEX = "complex"


class ToolMode(str, Enum):
    """Chế độ tool cho một câu hỏi chatbot."""

    RAG = "rag"
    MCP = "mcp"
    BOTH = "both"
    NONE = "none"  # SIMPLE chat — không gọi RAG/MCP


@dataclass(frozen=True)
class ToolDecision:
    """Kết quả nhận diện tool cần dùng."""

    mode: ToolMode
    use_rag: bool
    use_mcp: bool
    use_mcp_products: bool
    use_mcp_store: bool
    use_mcp_promo: bool
    use_mcp_faq: bool
    reason: str


NO_TOOLS_DECISION = ToolDecision(
    mode=ToolMode.NONE,
    use_rag=False,
    use_mcp=False,
    use_mcp_products=False,
    use_mcp_store=False,
    use_mcp_promo=False,
    use_mcp_faq=False,
    reason="Tin nhắn SIMPLE — trả lời ngắn, không dùng RAG/MCP",
)


def load_prompt_file(filename: str, default: str = "") -> str:
    """Nạp nội dung prompt từ file .txt.

    Tự động quét các thư mục prompts hoặc services để đọc file mới nhất.
    """
    for p_dir in PROMPT_DIRS:
        file_path = p_dir / filename
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8").strip()
                if content:
                    return content
            except Exception as exc:
                logger.warning("Không thể đọc file prompt '%s': %s", file_path, exc)
    return default.strip()


def get_system_prompt(role: Optional[str] = None) -> str:
    """Lấy System Prompt theo vai trò người dùng từ file text tương ứng:

    - admin: system_prompt_admin.txt
    - customer / user: system_prompt_user.txt
    - public / khách vãng lai: system_prompt_public.txt Fallback về
    system_prompt.txt nếu chưa tìm thấy.
    """
    role_normalized = (role or "public").strip().lower()
    if role_normalized == "admin":
        prompt = load_prompt_file("system_prompt_admin.txt")
        if prompt:
            return prompt
    elif role_normalized in ("customer", "user"):
        prompt = load_prompt_file("system_prompt_user.txt")
        if prompt:
            return prompt
    else:
        prompt = load_prompt_file("system_prompt_public.txt")
        if prompt:
            return prompt

    # Fallback chung từ file system_prompt.txt
    fallback_sys = load_prompt_file("system_prompt.txt")
    if fallback_sys:
        return fallback_sys

    return (
        "Bạn là Chuyên viên tư vấn thời trang AI (Fashion AI Stylist) của Fashion Store AI. "
        "Hãy tư vấn trang phục, gợi ý size, chất liệu và giải đáp chính sách cửa hàng bằng tiếng Việt."
    )


# Hằng số SYSTEM_PROMPT mặc định (nạp từ file txt)
SYSTEM_PROMPT = get_system_prompt("public")


POLICY_KEYWORDS = (
    "chính sách",
    "đổi trả",
    "hoàn tiền",
    "giao hàng",
    "vận chuyển",
    "phí ship",
    "freeship",
    "ship",
    "địa chỉ",
    "hotline",
    "giờ mở",
    "liên hệ",
    "bảo hành",
    "thanh toán",
    "cửa hàng",
    "faq",
)

PROMO_KEYWORDS = (
    "khuyến mãi",
    "mã giảm",
    "voucher",
    "coupon",
    "promo",
    "giảm giá",
    "ưu đãi",
)

PRODUCT_KEYWORDS = (
    "áo",
    "quần",
    "váy",
    "đầm",
    "giày",
    "dép",
    "túi",
    "phụ kiện",
    "khoác",
    "sơ mi",
    "thun",
    "polo",
    "jean",
    "denim",
    "blazer",
    "hoodie",
    "size",
    "màu",
    "giá",
    "mua",
    "gợi ý",
    "tư vấn",
    "phối đồ",
    "mix",
    "match",
    "sản phẩm",
    "hàng",
    "mẫu",
    "outfit",
    "set đồ",
)

RAG_KNOWLEDGE_KEYWORDS = (
    "phối",
    "mix",
    "match",
    "outfit",
    "phong cách",
    "style",
    "chất liệu",
    "vải",
    "mặc",
    "đi làm",
    "đi chơi",
    "dự tiệc",
    "mùa hè",
    "mùa đông",
    "tư vấn",
    "nên chọn",
    "hợp với",
)

GREETING_ONLY = {
    "xin chào",
    "chào",
    "hello",
    "hi",
    "hey",
    "chào bạn",
    "alo",
}

THANKS_BYE = {
    "cảm ơn",
    "cam on",
    "thanks",
    "thank you",
    "tạm biệt",
    "bye",
    "goodbye",
    "ok",
    "okay",
    "ừ",
    "uh",
    "vâng",
    "dạ",
    "nhé",
    "rồi",
}

CHITCHAT_KEYWORDS = (
    "thời tiết",
    "trời mưa",
    "trời nắng",
    "nóng quá",
    "lạnh quá",
    "buồn",
    "vui quá",
    "mệt quá",
    "ăn gì",
    "ngủ ngon",
    "bạn khỏe",
    "khỏe không",
    "làm gì đó",
)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _product_text(text: str) -> str:
    """Che cụm khuyến mãi để tránh khớp nhầm từ khóa sản phẩm như 'giá' trong 'giảm giá'."""
    masked = text
    for phrase in ("giảm giá", "mã giảm", "khuyến mãi", "ưu đãi"):
        masked = masked.replace(phrase, " ")
    return masked


def format_suggested_products(products: Optional[list[dict[str, Any]]] = None) -> str:
    """Chuỗi mô tả 3 sản phẩm đang hiển thị dưới chatbot để AI tư vấn khớp 100%."""
    if not products:
        return ""
    lines: list[str] = []
    for idx, product in enumerate(products, 1):
        price = product.get("sale_price") or product.get("price")
        lines.append(
            f"{idx}. {product.get('name', 'Sản phẩm')} — giá {price}đ"
            f" (id: {product.get('id', '')})"
        )
    return (
        "=== SẢN PHẨM ĐANG HIỂN THỊ CHO KHÁCH (bắt buộc tư vấn đúng danh sách này) ===\n"
        + "\n".join(lines)
        + "\nChỉ gợi ý/tư vấn đúng các sản phẩm trên, khớp tên và giá 100% với thẻ sản phẩm bên dưới.\n\n"
    )


def format_context_blocks(
    contexts: Optional[list[dict[str, Any]]],
    empty_text: str = "Không có dữ liệu bổ sung.",
) -> str:
    if not contexts:
        return empty_text
    return "\n\n".join(
        f"[Nguồn {idx + 1}] {item.get('text', '')}"
        for idx, item in enumerate(contexts)
    )


def is_shopping_intent(message: str) -> bool:
    """True khi câu hỏi mang ý định tìm/mua/gợi ý sản phẩm thời trang."""
    text = (message or "").strip().lower()
    if len(text) < 2 or text in GREETING_ONLY:
        return False

    product_text = _product_text(text)
    has_product = _contains_any(product_text, PRODUCT_KEYWORDS)
    has_policy = _contains_any(text, POLICY_KEYWORDS)
    has_promo = _contains_any(text, PROMO_KEYWORDS)
    if (has_policy or has_promo) and not has_product:
        return False
    return has_product


def is_mcp_structured_intent(message: str) -> bool:
    """True khi cần MCP tra cứu cấu trúc: store info / promo / FAQ."""
    text = (message or "").strip().lower()
    if len(text) < 2 or text in GREETING_ONLY:
        return False
    return _contains_any(text, POLICY_KEYWORDS) or _contains_any(text, PROMO_KEYWORDS)


def is_rag_knowledge_intent(message: str) -> bool:
    """True khi câu hỏi nghiêng về tư vấn tri thức / phong cách (RAG)."""
    text = (message or "").strip().lower()
    if len(text) < 2 or text in GREETING_ONLY:
        return False
    product_text = _product_text(text)
    return _contains_any(text, RAG_KNOWLEDGE_KEYWORDS) or _contains_any(
        product_text, PRODUCT_KEYWORDS
    )


def classify_complexity_rules(message: str) -> Optional[ComplexityMode]:
    """Phân loại nhanh SIMPLE/COMPLEX bằng rule. None = chưa chắc, cần LLM."""
    text = (message or "").strip().lower()
    if len(text) < 2:
        return ComplexityMode.SIMPLE

    # Rõ ràng cần tool / tư vấn cửa hàng → COMPLEX
    if (
        is_shopping_intent(text)
        or is_mcp_structured_intent(text)
        or is_rag_knowledge_intent(text)
        or "faq" in text
        or "câu hỏi thường" in text
    ):
        return ComplexityMode.COMPLEX

    # Chào hỏi / cảm ơn / bye / tán gẫu ngoài shop → SIMPLE
    if text in GREETING_ONLY or text in THANKS_BYE:
        return ComplexityMode.SIMPLE
    if any(g in text for g in GREETING_ONLY) and len(text) <= 40:
        return ComplexityMode.SIMPLE
    if any(t in text for t in THANKS_BYE) and len(text) <= 40:
        return ComplexityMode.SIMPLE
    if _contains_any(text, CHITCHAT_KEYWORDS):
        return ComplexityMode.SIMPLE

    # Câu rất ngắn, không dính fashion keywords → SIMPLE
    if len(text) <= 24 and not _contains_any(_product_text(text), PRODUCT_KEYWORDS):
        return ComplexityMode.SIMPLE

    return None


def build_complexity_detection_prompt(message: str) -> str:
    """Nạp simple_mode_detection_prompt.txt để nhờ LLM gắn nhãn SIMPLE/COMPLEX."""
    template = load_prompt_file("simple_mode_detection_prompt.txt")
    if template and "{user_prompt}" in template:
        try:
            return template.format(user_prompt=message)
        except Exception as exc:
            logger.warning("Lỗi format simple_mode_detection_prompt.txt: %s", exc)
    return (
        "Phân loại tin nhắn sau là SIMPLE hoặc COMPLEX. Chỉ trả về một từ.\n\n"
        f"{message}"
    )


async def detect_message_complexity(
    message: str,
    llm: Any = None,
) -> ComplexityMode:
    """Gắn simple_mode_detection_prompt vào agent: rule trước, LLM khi mơ hồ."""
    ruled = classify_complexity_rules(message)
    if ruled is not None:
        return ruled

    if llm is not None:
        try:
            prompt = build_complexity_detection_prompt(message)
            raw = await llm.generate(prompt, system=None, temperature=0.0)
            label = (raw or "").strip().upper().replace(".", " ")
            first = label.split()[0] if label else ""
            if first == "SIMPLE" or label.startswith("SIMPLE"):
                return ComplexityMode.SIMPLE
            if first == "COMPLEX" or "COMPLEX" in label:
                return ComplexityMode.COMPLEX
            if "SIMPLE" in label:
                return ComplexityMode.SIMPLE
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM complexity detection failed: %s", exc)

    # Mặc định COMPLEX để không bỏ sót câu hỏi cửa hàng
    return ComplexityMode.COMPLEX


def simple_fallback_answer(message: str) -> str:
    """Fallback khi LLM trống ở chế độ SIMPLE."""
    text = (message or "").strip().lower()
    if text in GREETING_ONLY or any(g in text for g in GREETING_ONLY):
        return (
            "Xin chào! Mình là Fashion AI Stylist của cửa hàng. "
            "Bạn muốn tư vấn sản phẩm, phối đồ, chọn size hay hỏi khuyến mãi không ạ?"
        )
    if _contains_any(text, CHITCHAT_KEYWORDS):
        return (
            "Mình là stylist thời trang nên không theo dõi thời tiết/chuyện phiếm chi tiết, "
            "nhưng mình sẵn sàng gợi ý outfit phù hợp ngày hôm nay cho bạn nhé!"
        )
    if text in THANKS_BYE or any(t in text for t in THANKS_BYE):
        return "Dạ không có chi! Bạn cần tư vấn thêm sản phẩm hay chính sách cửa hàng cứ hỏi mình nhé."
    return (
        "Mình có thể giúp bạn tìm đồ, phối outfit, chọn size hoặc giải đáp khuyến mãi/chính sách. "
        "Bạn muốn hỏi gì ạ?"
    )


def detect_tool_mode(message: str) -> ToolDecision:
    """Nhận biết nên dùng RAG, MCP, hay cả hai cho câu hỏi hiện tại.

    Quy ước:
    - MCP: hỏi chính sách / hotline / KM / FAQ cần tra cứu có cấu trúc.
    - RAG: hỏi tri thức thời trang, phối đồ, tư vấn chung từ kho vector.
    - BOTH: tìm/mua/gợi ý sản phẩm (RAG ngữ cảnh + MCP product_search),
      hoặc vừa hỏi sản phẩm vừa hỏi chính sách/KM.
    """
    text = (message or "").strip().lower()
    shopping = is_shopping_intent(text)
    has_policy = _contains_any(text, POLICY_KEYWORDS)
    has_promo = _contains_any(text, PROMO_KEYWORDS)
    has_faq = "faq" in text or "câu hỏi thường" in text
    mcp_structured = has_policy or has_promo or has_faq
    rag_knowledge = is_rag_knowledge_intent(text)

    use_mcp_products = shopping
    use_mcp_promo = has_promo
    use_mcp_store = has_policy and not has_promo
    use_mcp_faq = has_faq or (has_policy and not has_promo)
    use_mcp = use_mcp_products or mcp_structured

    # Sản phẩm / mua sắm: luôn BOTH (RAG + MCP product_search)
    if shopping and mcp_structured:
        return ToolDecision(
            mode=ToolMode.BOTH,
            use_rag=True,
            use_mcp=True,
            use_mcp_products=True,
            use_mcp_store=use_mcp_store,
            use_mcp_promo=use_mcp_promo,
            use_mcp_faq=use_mcp_faq,
            reason="Vừa hỏi sản phẩm vừa hỏi chính sách/khuyến mãi → RAG + MCP",
        )

    if shopping:
        return ToolDecision(
            mode=ToolMode.BOTH,
            use_rag=True,
            use_mcp=True,
            use_mcp_products=True,
            use_mcp_store=False,
            use_mcp_promo=False,
            use_mcp_faq=False,
            reason="Tìm/gợi ý sản phẩm → RAG (ngữ cảnh) + MCP product_search",
        )

    if mcp_structured and not rag_knowledge:
        return ToolDecision(
            mode=ToolMode.MCP,
            use_rag=False,
            use_mcp=True,
            use_mcp_products=False,
            use_mcp_store=use_mcp_store or has_policy,
            use_mcp_promo=use_mcp_promo,
            use_mcp_faq=use_mcp_faq,
            reason="Hỏi chính sách/KM/FAQ có cấu trúc → chỉ MCP",
        )

    if mcp_structured and rag_knowledge:
        return ToolDecision(
            mode=ToolMode.BOTH,
            use_rag=True,
            use_mcp=True,
            use_mcp_products=False,
            use_mcp_store=use_mcp_store or has_policy,
            use_mcp_promo=use_mcp_promo,
            use_mcp_faq=use_mcp_faq,
            reason="Vừa tư vấn tri thức vừa cần dữ liệu cấu trúc → RAG + MCP",
        )

    # Mặc định / chào hỏi / tư vấn chung: RAG
    return ToolDecision(
        mode=ToolMode.RAG,
        use_rag=True,
        use_mcp=False,
        use_mcp_products=False,
        use_mcp_store=False,
        use_mcp_promo=False,
        use_mcp_faq=False,
        reason="Tư vấn tri thức / hội thoại chung → chỉ RAG",
    )


def _render_template(
    filename: str,
    *,
    history_block: str,
    context: str = "",
    mcp_context: str = "",
    suggested_block: str,
    question: str,
) -> Optional[str]:
    template = load_prompt_file(filename)
    if not template or "{question}" not in template:
        return None
    try:
        return template.format(
            history_block=history_block,
            context=context,
            mcp_context=mcp_context,
            suggested_block=suggested_block,
            question=question,
        )
    except Exception as exc:
        logger.warning("Lỗi định dạng template %s: %s", filename, exc)
        return None


def build_rag_prompt(
    question: str,
    contexts: list[dict[str, Any]],
    history_text: str = "",
    suggested_products: Optional[list[dict[str, Any]]] = None,
) -> str:
    """Prompt khi chỉ dùng RAG."""
    history_block = (
        f"=== BỘ NHỚ HỘI THOẠI (WORKING / EPISODIC / SEMANTIC / LONG_TERM) ===\n{history_text}\n\n"
        if history_text
        else ""
    )
    suggested_block = format_suggested_products(suggested_products)
    context_text = format_context_blocks(
        contexts,
        empty_text="Không tìm thấy thêm thông tin bổ sung trong cửa hàng.",
    )

    rendered = _render_template(
        "rag_prompt.txt",
        history_block=history_block,
        context=context_text,
        suggested_block=suggested_block,
        question=question,
    )
    if rendered:
        return rendered

    return (
        "Bạn là trợ lý AI Stylist của cửa hàng thời trang Fashion Store AI.\n"
        "Hãy trả lời bằng tiếng Việt, thân thiện và hữu ích.\n\n"
        f"{history_block}"
        f"=== THÔNG TIN THỰC TẾ TỪ CỬA HÀNG (RAG) ===\n{context_text}\n\n"
        f"{suggested_block}"
        f"=== CÂU HỎI CỦA KHÁCH HÀNG ===\n{question}\n\n"
        "Trả lời:"
    )


def build_mcp_prompt(
    question: str,
    mcp_contexts: list[dict[str, Any]],
    history_text: str = "",
    suggested_products: Optional[list[dict[str, Any]]] = None,
) -> str:
    """Prompt khi chỉ dùng MCP tools."""
    history_block = (
        f"=== BỘ NHỚ HỘI THOẠI (WORKING / EPISODIC / SEMANTIC / LONG_TERM) ===\n{history_text}\n\n"
        if history_text
        else ""
    )
    suggested_block = format_suggested_products(suggested_products)
    mcp_text = format_context_blocks(
        mcp_contexts,
        empty_text="Không có dữ liệu trả về từ MCP tools.",
    )

    rendered = _render_template(
        "mcp_prompt.txt",
        history_block=history_block,
        mcp_context=mcp_text,
        suggested_block=suggested_block,
        question=question,
    )
    if rendered:
        return rendered

    return (
        "Bạn là trợ lý AI Stylist, trả lời dựa trên dữ liệu MCP tools.\n"
        "Hãy trả lời bằng tiếng Việt, chính xác theo dữ liệu được cung cấp.\n\n"
        f"{history_block}"
        f"=== DỮ LIỆU TỪ MCP TOOLS ===\n{mcp_text}\n\n"
        f"{suggested_block}"
        f"=== CÂU HỎI CỦA KHÁCH HÀNG ===\n{question}\n\n"
        "Trả lời:"
    )


def build_hybrid_prompt(
    question: str,
    rag_contexts: list[dict[str, Any]],
    mcp_contexts: list[dict[str, Any]],
    history_text: str = "",
    suggested_products: Optional[list[dict[str, Any]]] = None,
) -> str:
    """Dùng cả prompt RAG + prompt MCP khi chạy cả hai tool."""
    rag_part = build_rag_prompt(
        question,
        rag_contexts,
        history_text=history_text,
        suggested_products=None,  # suggested chỉ gắn 1 lần ở MCP part
    )
    mcp_part = build_mcp_prompt(
        question,
        mcp_contexts,
        history_text="",  # tránh lặp history
        suggested_products=suggested_products,
    )

    # Bỏ phần "Câu trả lời:" cuối của rag_part; ghép hướng dẫn MCP phía sau
    rag_core = rag_part.rsplit("Câu trả lời:", 1)[0].rstrip()
    mcp_core = mcp_part
    # Bỏ history rỗng / trùng phần câu hỏi ở mcp nếu cần — giữ nguyên block MCP đầy đủ
    return (
        "=== CHẾ ĐỘ HYBRID: DÙNG CẢ RAG + MCP ===\n"
        "Hãy kết hợp kho tri thức (RAG) và dữ liệu công cụ (MCP) để trả lời nhất quán.\n\n"
        f"{rag_core}\n\n"
        "----------\n\n"
        f"{mcp_core}"
    )


def build_shopping_prompt(
    question: str,
    contexts: list[dict[str, Any]],
    history_text: str = "",
    role: Optional[str] = None,
    suggested_products: Optional[list[dict[str, Any]]] = None,
    tool_mode: Optional[ToolMode | str] = None,
    mcp_contexts: Optional[list[dict[str, Any]]] = None,
) -> str:
    """Xây dựng prompt theo tool_mode: rag | mcp | both.

    - rag: rag_prompt.txt
    - mcp: mcp_prompt.txt
    - both: ghép cả hai prompt RAG + MCP
    - none: không dùng hàm này (agent trả lời bằng simple_fallback_answer)
    """
    _ = role  # giữ tương thích chữ ký cũ
    mode = ToolMode(tool_mode) if tool_mode else None
    if mode is None:
        mode = detect_tool_mode(question).mode

    if mode == ToolMode.NONE:
        return simple_fallback_answer(question)

    rag_contexts = contexts or []
    mcp_ctx = mcp_contexts if mcp_contexts is not None else []

    if mode == ToolMode.MCP:
        # Nếu caller chỉ truyền contexts chung, coi đó là mcp_contexts
        effective_mcp = mcp_ctx or rag_contexts
        return build_mcp_prompt(
            question,
            effective_mcp,
            history_text=history_text,
            suggested_products=suggested_products,
        )

    if mode == ToolMode.BOTH:
        return build_hybrid_prompt(
            question,
            rag_contexts,
            mcp_ctx,
            history_text=history_text,
            suggested_products=suggested_products,
        )

    return build_rag_prompt(
        question,
        rag_contexts,
        history_text=history_text,
        suggested_products=suggested_products,
    )


def fallback_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    """Câu trả lời dự phòng khi AI không khả dụng, trích xuất trực tiếp từ FAQ

    truy xuất được.
    """
    if contexts:
        snippets = [ctx["text"][:220] for ctx in contexts[:2]]
        joined = "\n- ".join(snippets)
        return (
            "Dựa trên dữ liệu cửa hàng hiện có, mình tìm thấy thông tin liên"
            f" quan:\n- {joined}\n\nBạn có thể hỏi thêm về màu sắc, kích cỡ, giá"
            " hoặc khuyến mãi để mình gợi ý chính xác hơn."
        )
    return (
        "Hiện trợ lý AI đang cập nhật kho tri thức thời trang. "
        "Bạn có thể hỏi về các mẫu áo, quần, váy, chọn size, giao hàng hoặc mã giảm giá nhé! "
        f'Câu hỏi của bạn: "{question}".'
    )
