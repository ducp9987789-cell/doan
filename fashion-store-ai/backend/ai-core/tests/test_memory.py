from memory.chat_memory import ChatMemory, MemoryKind


def test_working_overflow_moves_to_episodic():
    memory = ChatMemory(session_id="s1")
    memory.WORKING_LIMIT = 4
    for idx in range(6):
        memory.add_user(f"câu hỏi {idx} về áo")
        memory.add_assistant(f"trả lời {idx}")
    assert len(memory.working) == 4
    assert len(memory.episodic) >= 2
    assert all(item.kind == MemoryKind.EPISODIC.value for item in memory.episodic)


def test_semantic_and_long_term_from_user_facts():
    memory = ChatMemory(session_id="s2")
    memory.add_user("Mình cao 1m75 nặng 65kg, thích màu đen, size M")
    assert memory.semantic
    assert memory.long_term
    facts = memory.retrieve_semantic("chọn size áo", threshold=0.05)
    assert facts
    prompt = memory.as_prompt_context("gợi ý size áo")
    assert "LONG_TERM" in prompt or "SEMANTIC" in prompt
    assert "WORKING" in prompt


def test_system_logs_excluded_from_prompt():
    memory = ChatMemory(session_id="s3")
    memory.add_user("Xin áo sơ mi")
    memory.add_system("tool product_search ok", event="tools")
    prompt = memory.as_prompt_context("áo sơ mi")
    assert "product_search" not in prompt
    assert len(memory.system) == 1


def test_from_dict_backward_compatible_with_turns_only():
    memory = ChatMemory.from_dict(
        "legacy",
        {"turns": [{"role": "user", "content": "hello"}], "metadata": {}},
    )
    assert len(memory.working) == 1
    assert memory.working[0].content == "hello"
    payload = memory.to_dict()
    assert "working" in payload and "turns" in payload
