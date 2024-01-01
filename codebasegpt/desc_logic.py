import os
from dotenv import load_dotenv
from openai import OpenAI  # Assuming you have a Python package for OpenAI

from .utils import get_proj_state_path, load_proj_state, save_proj_state
from .code_utils import trim_code, remove_comments
from .app_state import AppState
from .proj_state import ProjState, FileState
from .token_utils import limit_string


def do_desc(app_state: AppState) -> bool:
    print("\nEnsuring descriptions for project files...")
    print("You can interrupt it (Ctrl-C) and then restart without losing results")

    load_dotenv()
    app_state.openai = OpenAI()

    proj_state_path = get_proj_state_path(app_state.app_config.proj_folder)
    if not os.path.exists(proj_state_path):
        proj_desc = ProjState(remove_comments=app_state.proj_config.remove_comments, files=[])
        save_proj_state(proj_desc, app_state.app_config.proj_folder)

    proj_state = load_proj_state(app_state.app_config.proj_folder)
    if proj_state.remove_comments != app_state.proj_config.remove_comments:
        proj_state.remove_comments = app_state.proj_config.remove_comments
        proj_state.files = []
        print("\nremoveComments changed, so refreshing all files...")

    proj_state.files = [file for file in proj_state.files if file.path in app_state.file_paths]
#   proj_state.files = proj_state.files.filter(file => app_state.file_paths.includes(file.path)) 
        
    def verbose_log(text: str = ''):
        if app_state.app_config.verbose_log:
            print(text)

    for i, file_path in enumerate(app_state.file_paths):
        full_path = os.path.join(app_state.proj_config.path, file_path)
        mtime = get_mtime(full_path)

        file_desc = next((f for f in proj_state.files if f.path == file_path), None)
        if file_desc and file_desc.mtime == mtime:
            continue  # File not changed

        verbose_log("\n**************************************************************")
        print(f"\nCreating description for: {file_path}")

        with open(full_path, 'r') as file:
            content = file.read()

        if app_state.proj_config.remove_comments:
            content = remove_comments(file_path, content)
        content = trim_code(content)

        desc = 'File is empty'
        embed : list[float] = []
        if len(content) > 0:
            verbose_log('\n******')
            verbose_log(content)

            sys_prompt = get_sys_prompt(get_words(len(content)), os.path.basename(file_path))
            verbose_log('\n******')
            verbose_log(f'sys prompt: {sys_prompt}')   
            
            verbose_log('\n******')
            print('waiting for model response...')

            content2 = limit_string(content, 15000)
            completion = app_state.openai.chat.completions.create(
                model=app_state.app_config.description_model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": content2}
                ],
                temperature=0
            )
            desc = completion.choices[0].message.content
            verbose_log('\n******')
            print(f'description: {desc}')

            content3 = limit_string(content, 8000)
            print('\ngenerating embedding...')
            embed_response = app_state.openai.embeddings.create(
                model="text-embedding-ada-002",
                input=[content3]
            )
            embed = embed_response.data[0].embedding
            print('done')

        proj_state.files = [f for f in proj_state.files if f.path != file_path]
        proj_state.files.append(FileState(path=file_path, mtime=mtime, desc=desc, embed=embed))

        # Sort results
        proj_state.files = [next((f for f in proj_state.files if f.path == p), None) for p in app_state.file_paths]
        proj_state.files = [f for f in proj_state.files if f is not None]
        save_proj_state(proj_state, app_state.app_config.proj_folder)

    print("\nDescriptions ready")
    app_state.proj_state = proj_state
    return True


def get_mtime(file_path: str) -> int:
    stats = os.stat(file_path)
    return int(stats.st_mtime)


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
    