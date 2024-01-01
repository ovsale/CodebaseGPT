model_pricing = [
    {
        'model': 'gpt-3.5-turbo-1106',
        'cost': [0.001, 0.002]
    },
    {
        'model': 'gpt-3.5-turbo-instruct',
        'cost': [0.0015, 0.002]
    },
    {
        'model': 'gpt-3.5-turbo',
        'cost': [0.001, 0.002]
    },
    {
        'model': 'gpt-4-1106-preview',
        'cost': [0.01, 0.03]
    },
    {
        'model': 'gpt-4-32k',
        'cost': [0.06, 0.12]
    },
    {
        'model': 'gpt-4',
        'cost': [0.03, 0.06]
    },
]

def get_cost(completion) -> float:
    return get_cost2(completion.model, completion.prompt_tokens, completion.completion_tokens)

def get_cost2(model: str, in_tokens: int, out_tokens: int) -> float:
    pricing = next((p for p in model_pricing if model.startswith(p['model'])), None)
    if pricing:
        return pricing['cost'][0] * (in_tokens / 1000) + pricing['cost'][1] * (out_tokens / 1000)
    return 0.0
