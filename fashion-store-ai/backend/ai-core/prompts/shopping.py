from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = (
    "You are Fashion Store AI shopping assistant using RAG context. "
    "Help customers choose fashion products, explain policies, and suggest items."
)


def build_shopping_prompt(
    question: str,
    contexts: list[dict[str, Any]],
    history_text: str = "",
) -> str:
    context_text = "\n\n".join(
        f"[Source {idx + 1}] {item.get('text', '')}" for idx, item in enumerate(contexts)
    ) or "No extra store knowledge found."
    history_block = f"Recent conversation:\n{history_text}\n\n" if history_text else ""
    return (
        "You are a helpful fashion store shopping assistant for Fashion Store AI.\n"
        "Answer in the same language as the customer question.\n"
        "Use the provided context about products, promotions, FAQ and policies.\n"
        "If the context is insufficient, say so politely and suggest browsing products.\n"
        "Keep answers concise and useful for shopping decisions.\n\n"
        f"{history_block}"
        f"Context:\n{context_text}\n\n"
        f"Customer question: {question}\n"
        "Assistant answer:"
    )


def fallback_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    if contexts:
        snippets = [ctx["text"][:220] for ctx in contexts[:2]]
        joined = "\n- ".join(snippets)
        return (
            "Dựa trên dữ liệu cửa hàng hiện có, mình tìm thấy thông tin liên quan:\n"
            f"- {joined}\n\n"
            "Bạn có thể hỏi thêm về màu sắc, kích cỡ, giá hoặc khuyến mãi để mình gợi ý chính xác hơn."
        )
    return (
        "Hiện chatbot đang chạy ở chế độ demo (chưa cấu hình API key LLM). "
        "Bạn có thể hỏi về sản phẩm, giá, màu sắc, kích cỡ, giao hàng hoặc khuyến mãi. "
        f"Câu hỏi của bạn: \"{question}\"."
    )
