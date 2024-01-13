import os
import pathspec
from typing import Optional

from codebasegpt.app_config import MODE_DESC, MODE_DESC_NO, MODE_DESC_2
from .app_config import AppConfig
from .proj_config import ProjConfig
from .app_const import data_root
from .app_state import AppState
from .input_utils import input_yes_no, is_no
from .init_utils import (
    compute_sizes, get_file_paths, get_proj_stat, list_project_files, load_gitignore, print_file_tree,
    print_proj_stat
)
from .utils import (
    ensure_folder, get_app_config_path, get_proj_config_path, get_proj_data_folder, load_app_config, load_proj_config,
    save_app_config, save_proj_config
)

def do_init(app_state: AppState) -> bool:
    ensure_folder(data_root)

    first_run = not os.path.exists(get_app_config_path())
    if first_run:
        save_app_config(AppConfig())

    app_config = load_app_config()
    print(f'\nApp settings:')
    print(f'Model to create file descriptions: {app_config.description_model}')
    print(f'Model to create file embeddings: {app_config.embedding_model}')
    print(f'Model to power chat with your code: {app_config.chat_model}')
    if app_config.base_url :
        print(f'Model base url: {app_config.base_url}')

    if first_run:
        print(f'\nYou can change settings in {get_app_config_path()} file.')
        edit_app_config = input_yes_no('\nDo you like to change settings? [Y/n]: ')
        if not is_no(edit_app_config):
            print(f'\nEdit {get_app_config_path()} and RESTART app.')
            return False

    new_project = False
    if app_config.proj_folder == '':
        project_path = enter_project_path()
        new_project = set_current_project(app_config, project_path)
    else:
        print()
        proj_config = load_proj_config(app_config.proj_folder)
        same_project = input_yes_no(f'Continue with project {proj_config.path}? [Y/n]: ')
        if is_no(same_project):
            project_path = enter_project_path()
            new_project = set_current_project(app_config, project_path)
    
    proj_config = load_proj_config(app_config.proj_folder)
    if proj_config.desc_mode != MODE_DESC \
            and proj_config.desc_mode != MODE_DESC_NO \
            and proj_config.desc_mode != MODE_DESC_2 :
        print(f'ERROR: Wrong sys_prompt_mode value: {proj_config.desc_mode}')
        return False

    gitignore = pathspec.PathSpec.from_lines('gitwildmatch', [])
    if proj_config.gitignore:
        gitignore = load_gitignore(proj_config.path)

    files = list_project_files(proj_config.path, proj_config.include, proj_config.exclude, gitignore)
    compute_sizes(proj_config.path, files, proj_config.remove_comments)

    print('\nFiles will be included:')
    print_file_tree(files)

    project_stat = get_proj_stat(files)
    print()
    print_proj_stat(project_stat, proj_config.remove_comments)

    warnings = []
    if project_stat.file_count > 500:
        warnings.append('Warning: The total number of files > 500')
    if project_stat.total_size > 1000000:
        warnings.append('Warning: The total size of all files > 1 MB')
    if project_stat.large_files and project_stat.large_files[0]["size"] > 100000:
        warnings.append('Warning: At least one file is larger than 100 KB')
    if warnings:
        print()
        for warning in warnings:
            print(warning)
        print(
            '\nConsider to exclude more files if possible. '
            'This can help lower OpenAI API costs and maintain response quality.'
        )

    cont_next = input_yes_no('\nContinue with this project settings? [Y/n]: ')
    if is_no(cont_next):
        if new_project:
            print(
                f'\n'
                f'Edit the project configuration file: {get_proj_config_path(app_config.proj_folder)}.\n'
                f'\n'
                f'Specify the "include" and "exclude" fields with lists of glob patterns to determine which source folders '
                f'to include and which (test or resource) files to exclude.\n'
                f'Example configuration:\n'
                f'{{\n'
                f'    "include": ["src/**/*"],\n'
                f'    "exclude": ["src/test/**/*"]\n'
                f'}}\n'
                f'In this example, all files within the "src" directory are included, except for any files located '
                f'within the "src/test" directory.\n'
                f'\n'
                f'After saving changes, RESTART this app.'
            )
        else:
            print(f'\nEdit {get_proj_config_path(app_config.proj_folder)} and RESTART app.')
        return False

    app_state.app_config = app_config
    app_state.proj_config = proj_config
    app_state.file_paths = get_file_paths(files)

    return True


def enter_project_path() -> str:
    project_path = ''
    while True:
        project_path = input('\nEnter project path: ')
        if not is_folder_exist(project_path):
            print(f'Wrong project path: {project_path}')
            continue
        break
    return project_path


def is_folder_exist(path_to_check: str) -> bool:
    if os.path.exists(path_to_check):
        stat = os.stat(path_to_check)
        return stat.st_mode & 0o170000 == 0o040000
    return False


def set_current_project(app_config: AppConfig, project_path: str) -> bool:
    new_project = False
    proj_folder = find_project_folder(data_root, project_path)
    if proj_folder is None:
        proj_name = os.path.basename(project_path)
        proj_folder = find_available_proj_folder(data_root, proj_name)

        proj_config = ProjConfig()
        proj_config.path = project_path
        proj_config.include = app_config.default_project_include
        proj_config.exclude = app_config.default_project_exclude
        proj_config.gitignore = app_config.default_project_gitignore
        proj_config.remove_comments = app_config.default_project_remove_comments
        proj_config.desc_mode = app_config.default_project_desc_mode

        ensure_folder(get_proj_data_folder(proj_folder))
        save_proj_config(proj_config, proj_folder)

        new_project = True

    app_config.proj_folder = proj_folder
    save_app_config(app_config)

    return new_project


def find_project_folder(data_folder_path: str, project_path_to_find: str) -> Optional[str]:
    directories = [d for d in os.listdir(data_folder_path) if os.path.isdir(os.path.join(data_folder_path, d))]

    for dir in directories:
        config_path = get_proj_config_path(dir)
        if os.path.exists(config_path):
            proj_config = load_proj_config(dir)
            if proj_config.path == project_path_to_find:
                return dir

    return None


def find_available_proj_folder(base_dir: str, base_name: str) -> str:
    counter = 2
    folder_name = base_name
    while os.path.exists(os.path.join(base_dir, folder_name)):
        folder_name = f'{base_name}{counter}'
        counter += 1
    return folder_name
