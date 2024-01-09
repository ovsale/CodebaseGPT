import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from codebasegpt.pack_files import PackFiles
# from openai.types.chat import ChatCompletionMessage

from .app_state import AppState
from codebasegpt import app_config 
from .token_utils import get_tokens_cnt
from .cost_utils import get_cost2
from .proj_state import FileState
from .code_utils import remove_comments, trim_code
from .input_utils import input_yes_no, is_no


find_page_size : int = 10
find_page_max_lines : int = 5

request_in_tokens : int = 0
request_out_tokens : int = 0
total_in_tokens : int = 0
total_out_tokens : int = 0

app_state = None


def do_chat(app_state_: AppState):
    global app_state
    app_state = app_state_

    exit_ = None
    messages = []

    def get_user_input():
        nonlocal messages
        while True:
            print()
            user_input = input('👤 You: ')

            # check for command
            user_input2 = user_input.strip().lower()
            if user_input2 == '/exit':
                nonlocal exit_
                exit_ = False
                return
            elif user_input2 == '/clear':
                messages = [messages[0]]
                print()
                print('Message history cleared')
                continue
            break

        messages.append({
            'role': 'user',
            'content': user_input
        })

    sys_prompt = get_sys_prompt(app_state.proj_config.sys_prompt_mode)

    messages.append({
        'role': 'system',
        'content': sys_prompt,
    })

    verbose_log('\n*** system prompt:')
    verbose_log(sys_prompt)
    verbose_log('*** end of system prompt')

    sys_prompt_tokens = get_tokens_cnt(sys_prompt)
    sys_prompt_cost = get_cost2(app_state.app_config.chat_model, sys_prompt_tokens, 0)
    print()
    print(f"System prompt input cost: ${sys_prompt_cost:.2f} ({sys_prompt_tokens} tokens)")

    print()
    print(f"Now you can ask questions about {os.path.basename(app_state.proj_config.path)} project. " +
        "Press Ctrl-C to interrupt at any time")

    get_user_input()

    while exit_ is None:
        print()
        print('Waiting for model response...')

        response = app_state.openai.chat.completions.create(
            model = app_state.app_config.chat_model,
            messages = messages,
            tools = get_tools(),
            temperature = 0
        )

        in_tokens = response.usage.prompt_tokens
        out_tokens = response.usage.completion_tokens
        global request_in_tokens, request_out_tokens
        request_in_tokens += in_tokens
        request_out_tokens += out_tokens
        global total_in_tokens, total_out_tokens
        total_in_tokens += in_tokens
        total_out_tokens += out_tokens

        response_message = response.choices[0].message   # ChatCompletionMessage
        messages.append(response_message.model_dump(exclude_none=True))

        if response_message.tool_calls ==  None:
            chat_tokens = sum(get_message_tokens(message) for message in messages[1:])
            chat_cost = get_cost2(app_state.app_config.chat_model, chat_tokens, 0)

            request_cost_in = get_cost2(app_state.app_config.chat_model, request_in_tokens, 0)
            request_cost_out = get_cost2(app_state.app_config.chat_model, 0, request_out_tokens)
            total_cost = get_cost2(app_state.app_config.chat_model, total_in_tokens, total_out_tokens)

            print()
            print(f"Next input cost: ${(sys_prompt_cost + chat_cost):.2f} "
                  f"(system: ${sys_prompt_cost:.2f}, chat: ${chat_cost:.2f})")
            print(f"Request cost: ${(request_cost_in + request_cost_out):.2f} "
                  f"(input: ${request_cost_in:.2f}, output: ${request_cost_out:.2f})")
            print(f"Session cost: ${total_cost:.2f}")

            print()
            print(f'🤖 Bot: {response_message.content}')

            request_in_tokens = 0
            request_out_tokens = 0

            get_user_input()
        else:
            if response_message.content is not None:
                print()
                print(f'🤖 Bot: {response_message.content}')
            for i in range(len(response_message.tool_calls)):
                tool_call = response_message.tool_calls[i]

                result = call_function(tool_call.function)

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': json.dumps(result),
                })

    return exit_


def verbose_log(text=''):
    if app_state.app_config.verbose_log:
        print(text)


def get_sys_prompt(sys_prompt_mode: str):
    if (sys_prompt_mode == app_config.MODE_DESC):
        return get_sys_prompt1()
    if (sys_prompt_mode == app_config.MODE_DESC_NO):
        return get_sys_prompt2()
    if (sys_prompt_mode == app_config.MODE_DESC_2):
        return get_sys_prompt3()
    raise ValueError(f"wrong value: {sys_prompt_mode}")


def get_sys_prompt1():
    proj_struct = get_sys_context1(app_state.proj_state.files)

    proj_name = os.path.basename(app_state.proj_config.path)
    sys_prompt = (f"You are the chat bot with task to answer user questions about \"{proj_name}\" software project.\n"
                  "You find list of all project files with its descriptions below.\n"
                  "If you need to load content for some file please use \"get_file\" function.\n"
                  "You can search for files using 'find_files_semantic' function.\n"
                  "Also, you can search in files content using 'find_in_files' function.\n"
                  "You can also be asked to make changes in project: use update_file function to create new or update existing file.\n\n"
                  "Project files with its descriptions:\n\n"
                  f"{proj_struct}\n")
    return sys_prompt


def get_sys_context1(files: list[FileState]):
    return '\n\n'.join(f"{add_path_prefix(file.path)}\n{file.desc}" for file in files)


def get_sys_prompt2():
    proj_struct = get_sys_context2(app_state.packs)

    proj_name = os.path.basename(app_state.proj_config.path)
    sys_prompt = (f"You are the chat bot with task to answer user questions about \"{proj_name}\" software project.\n"
                  "You find list of all project folders with containing files below.\n"
                  "If you need to load content for some file please use \"get_file\" function.\n"
                  "You can search for files using 'find_files_semantic' function.\n"
                  "Also, you can search in files content using 'find_in_files' function.\n"
                  "You can also be asked to make changes in project: use update_file function to create new or update existing file.\n\n"
                  "Project folders with containing files:\n"
                  f"{proj_struct}\n")
    return sys_prompt


def get_sys_context2(packs: list[PackFiles]):
    return '\n'.join(packs_to_string(packs))


def packs_to_string(packs: list[PackFiles]) -> list[str]:
    result = []
    for pack in packs:
        result.append(f"\n./{pack.path}")
        result.extend([f"    {file}" for file in pack.files])
    return result


def get_sys_prompt3():
    proj_struct = get_sys_context3(app_state.packs, app_state.proj_state.files)

    proj_name = os.path.basename(app_state.proj_config.path)
    sys_prompt = (f"You are the chat bot with task to answer user questions about \"{proj_name}\" software project.\n"
                  "You find list of all project files with its descriptions below.\n"
                  "If you need to load content for some file please use \"get_file\" function.\n"
                  "You can search for files using 'find_files_semantic' function.\n"
                  "Also, you can search in files content using 'find_in_files' function.\n"
                  "You can also be asked to make changes in project: use update_file function to create new or update existing file.\n\n"
                  "Project files with its descriptions:\n\n"
                  f"{proj_struct}\n")
    return sys_prompt


def get_sys_context3(packs: list[PackFiles], files: list[FileState]):
    return '\n'.join(packs_to_string3(packs, files))


def packs_to_string3(packs: list[PackFiles], files: list[FileState]) -> list[str]:
    result = []
    for pack in packs:
        result.append(f"\n./{pack.path}")
        for file in pack.files:
            file_path = os.path.join(pack.path, file)
            file_state = next((f for f in files if f.path == file_path), None)
            desc2 = file_state.desc2 if file_state else ''
            result.append(f"    {file} - {desc2}")
    return result


def get_tools():
    return [
        {
            "type": 'function',
            "function": {
                "name": "get_file",
                "description": "Loads file content code for your inspection.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "path to file"
                        },
                    },
                    "required": [
                        "name",
                        "path",
                    ]
                }
            }
        },
        {
            "type": 'function',
            "function": {
                "name": "find_files_semantic",
                "description": "Search for files using semantic (embedding-based) search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "String to search for."
                        },
                        "page": {
                            "type": "integer",
                            "description": "Allows you to page through results. 0 = first page."
                        },
                    },
                    "required": [
                        "name",
                        "query",
                        "page",
                    ]
                }
            }
        },
        {
            "type": 'function',
            "function": {
                "name": "find_in_files",
                "description": "The function searches for query string in files content. logical operations, symbol escaping or regex not supported",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "String to search for."
                        },
                        "is_case_sensitive": {
                            "type": "boolean",
                            "description": "Is query is case sensitive."
                        },
                        "page": {
                            "type": "integer",
                            "description": "Allows you to page through results. 0 = first page."
                        },
                    },
                    "required": [
                        "name",
                        "query",
                        "is_case_sensitive",
                        "page",
                    ]
                }
            }
        },
        {
            "type": 'function',
            "function": {
                "name": "update_file",
                "description": "Updates or creates file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "path to file"
                        },
                        "content": {
                            "type": "string",
                            "description": "file content"
                        },
                    },
                    "required": [
                        "name",
                        "path",
                        "code",
                    ]
                }
            }
        },
    ]


def call_function(function_call):
    args = json.loads(function_call.arguments)
    function_name = function_call.name

    if function_name == 'get_file':
        return get_file_func(args['path'])
    elif function_name == 'find_files_semantic':
        return find_files_semantic_func(args['query'], args['page'])
    elif function_name == 'find_in_files':
        return find_in_files_func(args['query'], args['is_case_sensitive'], args['page'])
    elif function_name == 'update_file':
        return update_file_func(args['path'], args['content'])
    else:
        print()
        print(f'!!!!!!!!!!!!!!!!!!! wrong function name: {function_name}')
        return {
            'error': f'Wrong function name: {function_name}',
        }


def get_file_func(path2):
    print()
    print(f'get_file function, path: {path2}')

    path3 = remove_path_prefix(path2)
    if path3 not in app_state.file_paths:
        print()
        print(f'!!!!!!!!!!!!!!!!!!! wrong path: {path2}')
        return {
            'path': path2,
            'error': 'Wrong file path',
        }
    content = load_file_content(path2)

    print(f'returned {path2} file content')

    return {
        'path': path2,
        'content': content,
    }


def add_path_prefix(path2):
    return '.' + os.sep + path2


def remove_path_prefix(path2):
    if path2.startswith('.' + os.sep):
        return path2[2:]
    return path2


def load_file_content(file_path):
    full_path = os.path.join(app_state.proj_config.path, file_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        content = file.read()

    if app_state.proj_config.remove_comments:
        content = remove_comments(file_path, content)

    content = trim_code(content)
    return content


def find_files_semantic_func(query, page):
    print()
    print(f"find_files_semantic function, query: {query}, page: {page}")

    print('\ngenerating embedding for query...')
    embed_response = app_state.openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[query]
    )
    print('done')

    ref_embed = embed_response.data[0].embedding
    ref_embed_array = np.array(ref_embed).reshape(1, -1)
    sim_res = []
    for file in app_state.proj_state.files:
        if len(file.embed) != 0:
            file_embed_array = np.array(file.embed).reshape(1, -1)
            similarity_score = cosine_similarity(ref_embed_array, file_embed_array)[0][0]
            sim_res.append((similarity_score, file))

    sim_res.sort(key=lambda x: x[0], reverse=True)
    page_res = sim_res[page * find_page_size: (page + 1) * find_page_size]
    res_paths = [add_path_prefix(item[1].path) for item in page_res]

    print_find_semantic_result(res_paths)

    return res_paths


def print_find_semantic_result(res_paths):
    print('results:')
    for path in res_paths:
        print(path)


def find_in_files_func(query, is_case_sensitive, page):
    print()
    print(f"find_in_files function, query: {query}, isCaseSensitive: {is_case_sensitive}, page: {page}")

    results = []
    for file in app_state.proj_state.files:
        content = load_file_content(file.path)
        lines = content.split('\n')
        matched_lines = []

        for index, line in enumerate(lines):
            if line_matches(line, query, is_case_sensitive):
                line_number = str(index + 1).ljust(6)
                matched_lines.append(f"{line_number}{line}")

        if matched_lines:
            if len(matched_lines) > find_page_max_lines:
                delta = len(matched_lines) - find_page_max_lines
                matched_lines = matched_lines[:find_page_max_lines] + [f"and {delta} more..."]

            results.append({
                'path': file.path,
                'occurrences': matched_lines,
            })

    page_results = results[page * find_page_size: (page + 1) * find_page_size]

    print_find_in_files_result(page_results)

    return page_results


def line_matches(line, query, is_case_sensitive):
    if is_case_sensitive:
        return query in line
    else:
        return query.lower() in line.lower()


def print_find_in_files_result(results):
    print('result:')
    for file in results:
        print(file['path'])

        for index, occurrence in enumerate(file['occurrences']):
            print(f"     {occurrence}")

    if not results:
        print('Nothing found')


def update_file_func(path2, code):
    print(f'\nupdate_file function, path: {path2}')

    if is_no(input_yes_no(f'Model wish to update file: {path2}, confirm? [Y/n]: ')):
        return {
            'error': f'User declined file update, path: {path2}',
        }

    path3 = remove_path_prefix(path2)
    full_path = os.path.join(app_state.proj_config.path, path3)

    folder_path = os.path.dirname(full_path)
    if not os.path.exists(folder_path) :
        print(f'\nERROR: Folder not exist, folder_path: {add_path_prefix(folder_path)}')
        return {
            'error': f'Folder not exist, folder_path: {add_path_prefix(folder_path)}',
        }

    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(code)

    print(f'file {path2} updated')

    return {
        'path': path2,
        'result': 'File updated',
    }


def get_message_tokens(message):
    content = message.get('content')
    if content is not None:
        return get_tokens_cnt(content)
    return 0




