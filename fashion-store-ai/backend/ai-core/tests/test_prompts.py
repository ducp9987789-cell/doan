from prompts.shopping import build_shopping_prompt, fallback_answer, is_shopping_intent


def test_build_shopping_prompt_includes_question_and_context():
    prompt = build_shopping_prompt(
        "Giá áo sơ mi?",
        [{"text": "Áo sơ mi trắng giá 249000 VND"}],
        suggested_products=[
            {"id": "1", "name": "Áo sơ mi trắng", "price": 249000, "sale_price": None},
        ],
    )
    assert "Giá áo sơ mi?" in prompt
    assert "249000" in prompt
    assert "Áo sơ mi trắng" in prompt
    assert "SẢN PHẨM ĐANG HIỂN THỊ" in prompt


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
