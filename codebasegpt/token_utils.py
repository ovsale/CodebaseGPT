from tiktoken import encoding_for_model


def get_tokens_cnt(text: str) -> int:
    encoder = encoding_for_model('gpt-3.5-turbo')
    return len(encoder.encode(text, disallowed_special=()))


def limit_string(text: str, max_tokens: int) -> str:
    encoder = encoding_for_model('gpt-3.5-turbo')
    tokens = encoder.encode(text, disallowed_special=())
    if len(tokens) > max_tokens:
        return encoder.decode(tokens[:max_tokens])
    return text
