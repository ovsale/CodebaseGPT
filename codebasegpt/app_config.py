from pydantic import BaseModel

MODE_DESC = "desc"
MODE_NO_DESC = "no_desc"
MODE_DESC_2 = "desc_2"

class AppConfig(BaseModel):
    proj_folder: str = ''
    sys_prompt_mode: str = MODE_DESC
    description_model: str = 'gpt-3.5-turbo-1106'
    chat_model: str = 'gpt-4-1106-preview'
    default_project_include: list[str] = ['**/*']
    default_project_exclude: list[str] = []
    default_project_gitignore: bool = True
    default_project_remove_comments: bool = False
    verbose_log: bool = False

