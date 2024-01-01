import json
import os
import re
from .app_config import AppConfig
from .proj_config import ProjConfig
from .proj_state import ProjState
from .app_const import data_root


# app

def load_app_config():
    with open(get_app_config_path(), 'r') as file:
        app_config_data = json.load(file)
    app_config = AppConfig.model_validate(app_config_data)
    return app_config


def save_app_config(app_config: AppConfig):
    with open(get_app_config_path(), 'w') as file:
        json.dump(app_config.model_dump(), file, indent=4)


def get_app_config_path():
    return os.path.join(data_root, 'app_config.json')


# proj

def load_proj_config(proj_folder: str):
    with open(get_proj_config_path(proj_folder), 'r') as file:
        proj_config_data = json.load(file)
    proj_config = ProjConfig.model_validate(proj_config_data)
    return proj_config


def save_proj_config(proj_config: ProjConfig, proj_folder: str):
    with open(get_proj_config_path(proj_folder), 'w') as file:
        json.dump(proj_config.model_dump(), file, indent=4)


def get_proj_config_path(proj_folder: str):
    return os.path.join(get_proj_data_folder(proj_folder), 'proj_config.json')


def load_proj_state(proj_folder: str):
    with open(get_proj_state_path(proj_folder), 'r') as file:
        proj_state_data = json.load(file)
    proj_state = ProjState.model_validate(proj_state_data)
    return proj_state


def save_proj_state(proj_state: ProjState, proj_folder: str):
    proj_state_json = json.dumps(proj_state.model_dump(), indent=4)
    proj_state_json = reformat_proj_state_json(proj_state_json)

    with open(get_proj_state_path(proj_folder), 'w') as file:
        file.write(proj_state_json)        


def reformat_proj_state_json(json_string):
    # Pattern to find array elements
    array_pattern = re.compile(r'"embed"\s*:\s*\[\s*(.*?)\s*\]', re.DOTALL)

    # Function to replace found arrays with single-line format
    def replace_array(match: re.Match):
        array_content = match.group(1)
        # Replace newlines and excessive spaces within arrays
        single_line_array = array_content.replace('\n', '')
        single_line_array = re.sub(r'\s+', ' ', single_line_array)
        return f'"embed": [{single_line_array}]'

    # Apply the replacement to the entire string
    return array_pattern.sub(replace_array, json_string)


def get_proj_state_path(proj_folder: str):
    return os.path.join(get_proj_data_folder(proj_folder), 'proj_state.json')


def get_proj_data_folder(proj_folder: str):
    return os.path.join(data_root, proj_folder)


# other

def ensure_folder(folder_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
