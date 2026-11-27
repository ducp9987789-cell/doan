import asyncio

from prompts.shopping import (
    ComplexityMode,
    ToolMode,
    build_mcp_prompt,
    build_shopping_prompt,
    classify_complexity_rules,
    detect_message_complexity,
    detect_tool_mode,
    fallback_answer,
    is_shopping_intent,
    simple_fallback_answer,
)


def test_build_shopping_prompt_includes_question_and_context():
    prompt = build_shopping_prompt(
        "Giá áo sơ mi?",
        [{"text": "Áo sơ mi trắng giá 249000 VND"}],
        suggested_products=[
            {"id": "1", "name": "Áo sơ mi trắng", "price": 249000, "sale_price": None},
        ],
        tool_mode=ToolMode.BOTH,
        mcp_contexts=[],
    )
    assert "Giá áo sơ mi?" in prompt
    assert "249000" in prompt
    assert "Áo sơ mi trắng" in prompt
    assert "SẢN PHẨM ĐANG HIỂN THỊ" in prompt
    assert "HYBRID" in prompt or "MCP" in prompt


def test_rag_prompt_mode():
    prompt = build_shopping_prompt(
        "Phối đồ mùa hè thế nào?",
        [{"text": "Nên chọn chất liệu cotton thoáng mát"}],
        tool_mode=ToolMode.RAG,
    )
    assert "Phối đồ mùa hè thế nào?" in prompt
    assert "cotton" in prompt
    assert "KHO TRI THỨC" in prompt or "RAG" in prompt


def test_mcp_prompt_mode():
    prompt = build_mcp_prompt(
        "Chính sách đổi trả?",
        [{"text": "Đổi trả trong 7 ngày"}],
    )
    assert "Chính sách đổi trả?" in prompt
    assert "7 ngày" in prompt
    assert "MCP" in prompt


def test_simple_fallback_answer():
    assert "Fashion AI Stylist" in simple_fallback_answer("Xin chào")
    assert "thời trang" in simple_fallback_answer("Thời tiết đẹp không").lower()


def test_detect_tool_mode():
    both = detect_tool_mode("Gợi ý áo sơ mi đi làm")
    assert both.mode == ToolMode.BOTH
    assert both.use_rag and both.use_mcp_products

    mcp = detect_tool_mode("Chính sách đổi trả là gì?")
    assert mcp.mode == ToolMode.MCP
    assert mcp.use_mcp and not mcp.use_rag

    promo = detect_tool_mode("Có mã giảm giá nào không?")
    assert promo.mode == ToolMode.MCP
    assert promo.use_mcp_promo


def test_complexity_simple_vs_complex():
    assert classify_complexity_rules("Xin chào") == ComplexityMode.SIMPLE
    assert classify_complexity_rules("thời tiết đẹp không") == ComplexityMode.SIMPLE
    assert classify_complexity_rules("cảm ơn") == ComplexityMode.SIMPLE
    assert classify_complexity_rules("Gợi ý áo sơ mi") == ComplexityMode.COMPLEX
    assert classify_complexity_rules("Chính sách đổi trả?") == ComplexityMode.COMPLEX

    assert asyncio.run(detect_message_complexity("Xin chào")) == ComplexityMode.SIMPLE
    assert asyncio.run(detect_message_complexity("Thời tiết đẹp không")) == ComplexityMode.SIMPLE
    assert asyncio.run(detect_message_complexity("Gợi ý áo sơ mi")) == ComplexityMode.COMPLEX


def test_shopping_intent_detects_product_vs_policy():
    assert is_shopping_intent("Gợi ý áo sơ mi đi làm")
    assert not is_shopping_intent("Chính sách đổi trả là gì?")
    assert not is_shopping_intent("Xin chào")


def test_fallback_answer_with_context():
    answer = fallback_answer("size?", [{"text": "Size S M L available"}])
    assert "Size S M L" in answer


def test_fallback_answer_without_context():
    answer = fallback_answer("hello", [])
    assert "kho tri thức" in answer.lower() or "thời trang" in answer.lower()
