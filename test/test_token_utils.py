from codebasegpt import token_utils as tu


def test_limit():
    long_text = "abc " * 1000
    max_tokens = 500
    limited_text = tu.limit_string(long_text, max_tokens)
    assert len(limited_text) < len(long_text)
    assert long_text.startswith(limited_text)


def test_not_limit():
    long_text = "abc " * 10
    max_tokens = 500
    limited_text = tu.limit_string(long_text, max_tokens)
    assert len(limited_text) == len(long_text)
    assert long_text == limited_text

