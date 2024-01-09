import os
from dotenv import load_dotenv
from openai import OpenAI

from codebasegpt import app_config 
from codebasegpt import utils
from codebasegpt import code_utils
from codebasegpt.app_state import AppState
from codebasegpt.proj_state import ProjState, FileState
from codebasegpt import token_utils


def do_desc(app_state: AppState) -> bool:
    print("\nEnsuring descriptions and embeddings for project files...")
    print("You can interrupt it (Ctrl-C) and then restart without losing results")

    load_dotenv()
    app_state.openai = OpenAI()

    proj_state_path = utils.get_proj_state_path(app_state.app_config.proj_folder)
    if not os.path.exists(proj_state_path):
        proj_state = ProjState(remove_comments=app_state.proj_config.remove_comments, files=[])
        utils.save_proj_state(proj_state, app_state.app_config.proj_folder)

    proj_state = utils.load_proj_state(app_state.app_config.proj_folder)
    if proj_state.remove_comments != app_state.proj_config.remove_comments:
        proj_state.remove_comments = app_state.proj_config.remove_comments
        proj_state.files = []
        print("\nremove_comments changed, so refreshing all files...")

    prev_len = len(proj_state.files)
    proj_state.files = [file for file in proj_state.files if file.path in app_state.file_paths]
    if prev_len != len(proj_state.files) :
        # some files was removed in project so save proj_state
        utils.save_proj_state(proj_state, app_state.app_config.proj_folder)

    for file_path in app_state.file_paths :
        full_path = os.path.join(app_state.proj_config.path, file_path)
        mtime = get_mtime(full_path)

        file_state = next((f for f in proj_state.files if f.path == file_path), None)
        if not file_state or file_state.mtime != mtime :
            # state not yet created or file content changed
            file_state = FileState(path=file_path, mtime=mtime, desc='', desc2='', embed=None)

        content = None
        if app_state.proj_config.desc_mode == app_config.MODE_DESC and file_state.desc == '' :
            content = get_file_content(content, file_path, app_state)
            sys_prompt = get_sys_prompt(get_words(len(content)), os.path.basename(file_path))
            file_state.desc = gen_desc(app_state, sys_prompt, content)

        if app_state.proj_config.desc_mode == app_config.MODE_DESC_2 and file_state.desc2 == '' :
            content = get_file_content(content, file_path, app_state)
            sys_prompt = get_sys_prompt2(get_words(len(content)) / 2)
            file_state.desc2 = gen_desc(app_state, sys_prompt, content)

        if file_state.embed == None :
            content = get_file_content(content, file_path, app_state)
            file_state.embed = gen_embed(app_state, content)

        if (content != None) :
            proj_state.files = [f for f in proj_state.files if f.path != file_path]
            proj_state.files.append(file_state)
            proj_state.files = sorted(proj_state.files,
                key=lambda file_state: app_state.file_paths.index(file_state.path))

            utils.save_proj_state(proj_state, app_state.app_config.proj_folder)

    print("\nDescriptions and embeddings ready")
    app_state.proj_state = proj_state
    return True


def get_mtime(file_path: str) -> int:
    stats = os.stat(file_path)
    return int(stats.st_mtime)


def get_file_content(content: str | None, file_path: str, app_state: AppState) -> str:
    if content != None :
        return content
    
    print(f"\nLoading file: {file_path}")

    full_path = os.path.join(app_state.proj_config.path, file_path)

    with open(full_path, 'r') as file:
        content = file.read()

    if app_state.proj_config.remove_comments:
        content = code_utils.remove_comments(file_path, content)

    return code_utils.trim_code(content)


def get_sys_prompt(words: int, name: str) -> str:
    return f"Create very condensed ({words} words) description of software project file {name}"


def get_words(size: int) -> int:
    if size < 300:
        return 20
    elif size < 1200:
        return 30
    elif size < 5000:
        return 40
    elif size < 20000:
        return 50
    else:
        return 60


def get_sys_prompt2(words: int) -> str:
    return f"""
Create very condensed ({words} words), one line description of a file
"""


def gen_desc(app_state : AppState, sys_prompt : str, content : str) -> str :
    if content == '' :
        return 'File is empty'
    
    content2 = token_utils.limit_string(content, 15000)
    print('Creating description, waiting for model response...')
    completion = app_state.openai.chat.completions.create(
        model=app_state.app_config.description_model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": content2}
        ],
        temperature=0
    )
    desc = completion.choices[0].message.content
    print(f'Description: {desc}')
    return desc


def gen_embed(app_state : AppState, content : str) -> list[float] :
    if content == '' :
        return []
    
    content2 = token_utils.limit_string(content, 8000)
    print('Generating embedding, waiting for model response...')
    embed_response = app_state.openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[content2]
    )
    print('Done')
    return embed_response.data[0].embedding

# def get_words2(size: int) -> int:
#     if size < 300:
#         return 15
#     elif size < 1200:
#         return 20
#     elif size < 5000:
#         return 25
#     elif size < 20000:
#         return 30
#     else:
#         return 30


# def get_sys_prompt2() -> str:
#     return f"""
# Create title for file. Just return title text no prefixes or quotes needed
# """


# def get_sys_prompt2(words: int, name: str) -> str:
#     return f"""
# Create very condensed ({words} words), one line description of software project file {name}
# """


# def get_words2(size: int) -> int:
#     if size < 300:
#         return 15
#     elif size < 1200:
#         return 20
#     elif size < 5000:
#         return 30
#     elif size < 20000:
#         return 30
#     else:
#         return 40


# def post_process_desc(desc2: str, file_name: str) -> str:
#     desc2 = remove_prefix(desc2, f"{file_name} ")
#     desc2 = remove_prefix(desc2, f"{file_name}: ")
#     desc2 = remove_prefix(desc2, f"{file_name} is a ")

#     _, ext = os.path.splitext(file_name)
#     ext = ext.lstrip('.')
#     if ext != '' :
#         lang = ext_to_lang(ext)
#         desc2 = remove_prefix(desc2, f"{lang} ")
#         desc2 = remove_prefix(desc2, f"A {lang} ")
#         desc2 = remove_prefix(desc2, f"is a {lang} ")

#     return capitalize(desc2)


# def capitalize(s: str) -> str:
#     if not s:
#         return s
#     return s[0].upper() + s[1:]


# def remove_prefix(text: str, prefix: str) -> str:
#     if text.lower().startswith(prefix.lower()):
#         return text[len(prefix):]
#     return text


# def ext_to_lang(ext: str) -> str:
#     if ext in ['js', 'jsx', 'mjs']:
#         return 'JavaScript'
#     elif ext in ['ts', 'tsx']:
#         return 'TypeScript'
#     elif ext == 'py':
#         return 'Python'
#     elif ext == 'md':
#         return 'MarkDown'
#     else:
#         return ext


# def get_sys_prompt3(name: str) -> str:
#     return f"""
# Your task is to shorten software project file description by excluding:
# 1) mentioning of its name: "{name}"
# 2) mentioning of its programming language (or file format)
# 3) mentioning fact that this file is part of software project
# Please remove this information if one or two or all is present 
# """


# def get_sys_prompt3(words: int, file_path: str) -> str:
#     return f"""
# Create very condensed ({words} words), one line description of software project file: {file_path}

# I like you to focus on aspects that not clear from its folder and name 

# Do not mention file name or it programming language in description. Call it file or module.
# """


# def get_sys_prompt4(words: int, name: str) -> str:
#     return f"""
# Create a very condensed ({words} words), one line description of a software project file {name}.
# Avoid mentioning the file name or its programming language. Refer to it as 'file' or 'module'.
# """



# def get_sys_prompt3(name: str) -> str:
#     return f"""
# Your task is remove from software project file description mentioning of its name: "{name}", programming language (file format) if it exist in description

# Examples:
# Input: 'MyTree.mjs' is a JavaScript module that defines a tree data structure with methods for adding, sorting, and retrieving nodes, as well as converting the tree to JSON format.
# Result: Defines a tree data structure with methods for adding, sorting, and retrieving nodes, as well as converting the tree to JSON format

# Input: The software project file TreeUtils.mjs provides functions for working with tree data structures, including retrieving node paths and checking parent-child relationships.
# Result: Provides functions for working with tree data structures, including retrieving node paths and checking parent-child relationships

# Input: This software project file creates a React component for rendering an arrow icon that toggles between open and closed states.
# Result: Creates a React component for rendering an arrow icon that toggles between open and closed states
# """


# def get_sys_prompt4(name: str) -> str:
#     return f"""
# Your task is to remove any mention of the software project's file name and its programming language
# if it is mentioned in the description. The goal is to retain the description of the functionality
# or purpose of the file but eliminate these specific details.

# For example:

# Input: MyTree.mjs is a JavaScript module that defines a tree data structure...
# Result: Defines a tree data structure with methods for adding, sorting, and retrieving nodes...

# Input: The file TreeUtils.mjs provides functions for working with tree data structures...
# Result: Provides functions for working with tree data structures...

# Input: This file creates a React component for rendering an arrow icon...
# Result: Creates a React component for rendering an arrow icon...

# Remember, the name and programming language can appear in different ways. Ensure you remove these irrespective
# of their format or position in the sentence.
# """


# def get_sys_prompt1(words: int, name: str) -> str:
#     return f"""
# Create a concise, {words}-word description outlining the primary function of a software project file {name}
# Try to keep main technology / framework names used in this file
# """


# def get_sys_prompt2(name: str) -> str:
#     return f"""
# Create a very condensed, one-sentence (20 words) description of the main purpose of a software project file '{name}'
# Please try to keep main technology / framework names used in this file
# """


# def get_sys_prompt3() -> str:
#     return f"""
# Your task is remove from software project file description mentioning of its name, programming language (file format) if it exist in description
# Examples:
# Input: The MyTree.mjs file contains a class for creating and managing a tree data structure with various operations.
# Result: class for creating and managing a tree data structure with various operations

# Input: The software project file TreeUtils.mjs provides functions for working with tree data structures, including retrieving node paths and checking parent-child relationships.
# Result: functions for working with tree data structures, including retrieving node paths and checking parent-child relationships

# Input: This software project file creates a React component for rendering an arrow icon that toggles between open and closed states.
# Result: React component for rendering an arrow icon that toggles between open and closed states
# """


    # return f"Provide a concise, 20-word description outlining the primary function of a software project file '{name}', excluding its name and programming language."
    