def input_yes_no(prompt: str) -> str:
    while True:
        user_input = input(prompt)
        if is_yes(user_input) or is_no(user_input) or is_default(user_input):
            return user_input
        else:
            print("Error: Please enter 'y', 'n', or empty for default")


def is_yes(input_str: str) -> bool:
    trimmed_input = input_str.strip().lower()
    return trimmed_input in ['y', 'yes', 'ok']


def is_no(input_str: str) -> bool:
    trimmed_input = input_str.strip().lower()
    return trimmed_input in ['n', 'no']


def is_default(input_str: str) -> bool:
    return input_str.strip() == ''
