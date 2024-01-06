import os
from wcmatch import glob
import pathspec
from typing import List

from codebasegpt.pack_files import PackFiles

from .file_node import FileNode
from .proj_stat import ProjStat
from .app_const import LARGE_SOURCE_FILE
from .code_utils import remove_comments
from .is_text_or_bin import is_text_file
from .pretty_bytes import bytes_to_str


def load_gitignore(root_path: str):
    gitignore_file = os.path.join(root_path, '.gitignore')
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'r') as f:
            return pathspec.PathSpec.from_lines('gitwildmatch', f.read().splitlines())
    else:
        print('No .gitignore found')
        return pathspec.PathSpec.from_lines('gitwildmatch', [])


def list_project_files(folder_path: str, include: list[str], exclude: list[str], gitignore: pathspec.PathSpec) -> list[FileNode]:
    files = build_file_tree(folder_path, folder_path, gitignore, include, exclude).folder_content
    files = remove_empty_folders(files)
    files = sort_file_data_alphabetically(files)
    return files


def build_file_tree(root_directory: str, directory: str, gitignore_spec: pathspec.PathSpec, include_patterns: list[str], exclude_patterns: list[str]):
    entries = os.listdir(directory)
    folder_content = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        relative_path = os.path.relpath(full_path, start=root_directory)

        # Check against .gitignore rules
        if gitignore_spec.match_file(relative_path):
            continue

        if os.path.isdir(full_path):
            folder_node = build_file_tree(root_directory, full_path, gitignore_spec, include_patterns, exclude_patterns)
            folder_content.append(folder_node)
        else:
            match_include = any(my_fnmatch(relative_path, pattern) for pattern in include_patterns)
            match_exclude = any(my_fnmatch(relative_path, pattern) for pattern in exclude_patterns)
            if not match_include or match_exclude:
                continue

            # if os.path.getsize(full_path) == 0:
            #     continue

            if not is_text_file(full_path):
                continue

            file_node = FileNode(entry, False, [], 0)
            folder_content.append(file_node)

    return FileNode(os.path.basename(directory), True, folder_content, 0)

def my_fnmatch(name: str, pat: str) -> bool:
    # return fnmatch.fnmatch(name, pat)
    return glob.globmatch(name, pat, flags=glob.GLOBSTAR)


def remove_empty_folders(file_data_array: list[FileNode]) -> list[FileNode]:
    def is_not_empty_folder(file_node: FileNode) -> bool:
        if file_node.is_folder:
            file_node.folder_content = remove_empty_folders(file_node.folder_content)
            return len(file_node.folder_content) > 0
        return True

    return list(filter(is_not_empty_folder, file_data_array))


def sort_file_data_alphabetically(files_data: list[FileNode]) -> list[FileNode]:
    # First, sort the current level alphabetically with folders first
    files_data.sort(key=lambda x: (not x.is_folder, x.name))

    # Then, recursively sort the contents of each folder
    for file_data in files_data:
        if file_data.is_folder:
            file_data.folder_content = sort_file_data_alphabetically(file_data.folder_content)

    return files_data


def compute_sizes(base_path: str, files: list[FileNode], remove_comments_: bool, current_path: str = '') -> int:
    total_size = 0
    for file in files:
        full_path = os.path.join(base_path, current_path, file.name)
        if file.is_folder:
            file.size = compute_sizes(base_path, file.folder_content, remove_comments_, os.path.join(current_path, file.name))
        else:
            if not remove_comments_:
                file.size = os.path.getsize(full_path)
            else:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = remove_comments(file.name, content)
                file.size = len(content.encode('utf-8'))
        total_size += file.size
    return total_size


def print_file_tree(files_data: list[FileNode], current_path: str = '', prefix: str = ''):
    for file in files_data:
        connector = '└── ' if file == files_data[-1] else '├── '
        new_prefix = prefix + ('    ' if file == files_data[-1] else '│   ')
        print(f'{current_path}{prefix}{connector}{file.name} ({bytes_to_str(file.size)})')
        if file.is_folder:
            print_file_tree(file.folder_content, current_path, new_prefix)


def get_proj_stat(file_data: list[FileNode]) -> ProjStat:
    stats = ProjStat(
        file_count=0,
        total_size=0,
        large_files=[]
    )
    def traverse_files(files: List[FileNode], current_path: str = ''):
        for file in files:
            full_path = current_path + file.name
            if file.is_folder:
                traverse_files(file.folder_content, full_path + '/')
            else:
                stats.file_count += 1
                stats.total_size += file.size
                if file.size > LARGE_SOURCE_FILE:
                    stats.large_files.append({'path': full_path, 'size': file.size})
    traverse_files(file_data)
    stats.large_files.sort(key=lambda x: x['size'], reverse=True)
    return stats


def print_proj_stat(proj_stat: ProjStat):
    print('Project summary:')
    print(f'Total number of files: {proj_stat.file_count}')
    print(f'Total size of files: {bytes_to_str(proj_stat.total_size)}')
    print(f'Large files included (> {bytes_to_str(LARGE_SOURCE_FILE)}):')
    if not proj_stat.large_files:
        print('  No large files')
    else:
        for index, file in enumerate(proj_stat.large_files):
            print(f'  {index + 1}. {file["path"]} - Size: {bytes_to_str(file["size"])}')


def get_file_paths(nodes: list[FileNode], current_path: str = '') -> List[str]:
    file_paths = []
    for node in nodes:
        full_path = current_path + node.name
        if node.is_folder:
            file_paths.extend(get_file_paths(node.folder_content, full_path + '/'))
        else:
            file_paths.append(full_path)
    return file_paths


def get_pack_files(files_data: list[FileNode], current_path: str = '') -> list[PackFiles]:
    files_data2 = sorted(files_data, key=lambda node: (node.is_folder, node.name))
    result : list[PackFiles] = []
    packFiles = None
    for node in files_data2:
        if node.is_folder:
            folder_path = f"{current_path}/{node.name}".lstrip('/')
            result.extend(get_pack_files(node.folder_content, current_path=folder_path))
        else:
            if not packFiles:
                packFiles = PackFiles(current_path, [])
                result.append(packFiles)

            packFiles.files.append(node.name)
    return result

