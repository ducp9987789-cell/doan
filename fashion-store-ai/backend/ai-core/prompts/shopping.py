from __future__ import annotations

import logging
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


def build_shopping_prompt(
    question: str,
    contexts: list[dict[str, Any]],
    history_text: str = "",
    role: Optional[str] = None,
) -> str:
    """Xây dựng prompt câu hỏi kết hợp kho tri thức (RAG) nạp từ file

    rag_prompt.txt.
    """
    context_text = "\n\n".join(
        f"[Nguồn {idx + 1}] {item.get('text', '')}"
        for idx, item in enumerate(contexts)
    ) or "Không tìm thấy thêm thông tin bổ sung trong cửa hàng."

    history_block = (
        f"=== LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY ===\n{history_text}\n\n"
        if history_text
        else ""
    )

    template = load_prompt_file("rag_prompt.txt")
    if template and "{context}" in template and "{question}" in template:
        try:
            return template.format(
                history_block=history_block,
                context=context_text,
                question=question,
            )
        except Exception as exc:
            logger.warning(
                "Lỗi định dạng template rag_prompt.txt: %s. Dùng mẫu chuẩn.", exc
            )

    # Mẫu dự phòng nếu template file bị thiếu placeholder
    return (
        "Bạn là trợ lý AI Stylist của cửa hàng thời trang Fashion Store AI.\n"
        "Hãy trả lời bằng tiếng Việt, thân thiện và hữu ích.\n\n"
        f"{history_block}"
        f"=== THÔNG TIN THỰC TẾ TỪ CỬA HÀNG ===\n{context_text}\n\n"
        f"=== CÂU HỎI CỦA KHÁCH HÀNG ===\n{question}\n\n"
        "Trả lời:"
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
