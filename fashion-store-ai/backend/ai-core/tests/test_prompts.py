from prompts.shopping import build_shopping_prompt, fallback_answer


def test_build_shopping_prompt_includes_question_and_context():
    prompt = build_shopping_prompt(
        "Giá áo sơ mi?",
        [{"text": "Áo sơ mi trắng giá 249000 VND"}],
    )
    assert "Giá áo sơ mi?" in prompt
    assert "249000" in prompt


def test_fallback_answer_with_context():
    answer = fallback_answer("size?", [{"text": "Size S M L available"}])
    assert "Size S M L" in answer


def test_fallback_answer_without_context():
    answer = fallback_answer("hello", [])
    assert "demo" in answer.lower() or "API key" in answer
