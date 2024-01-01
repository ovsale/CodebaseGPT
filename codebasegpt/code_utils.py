import re

def trim_code(text: str) -> str:
    lines = text.splitlines()
    result = []

    # replace more than 1 empty line with just 1 empty line
    for line in lines:
        if line.strip() == '' and (not result or result[-1].strip() == ''):
            continue
        result.append(line)

    # remove empty lines at the end of the file
    while result and result[-1].strip() == '':
        result.pop()

    return '\n'.join(result)


def remove_comments(file_name: str, file_content: str) -> str:
    file_extension = file_name.split('.')[-1]

    if file_extension in ['js', 'jsx', 'mjs', 'cjs', 'es', 'es6', 'ts', 'tsx', 'mts', 'java', 'c', 'h', 'cpp', 'cs']:
        # Remove single line and multi-line comments
        file_content = re.sub(r'/\*[\s\S]*?\*/', '', file_content)

        # Then remove full line and end-of-line comments
        lines = file_content.splitlines()
        lines = [line for line in lines if not line.strip().startswith('//')]
        lines = [line.split('//')[0].rstrip() for line in lines]
        return '\n'.join(lines)

    elif file_extension == 'css':
        return re.sub(r'/\*[\s\S]*?\*/', '', file_content)

    elif file_extension == 'html':
        return re.sub(r'<!--[^>]*-->', '', file_content)

    elif file_extension == 'py':
        lines = file_content.splitlines()
        lines = [line for line in lines if not line.strip().startswith('#')]
        lines = [line.split('#')[0].rstrip() for line in lines]
        return '\n'.join(lines)

    else:
        return file_content
