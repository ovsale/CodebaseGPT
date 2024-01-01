from pydantic import BaseModel

class AppConfig(BaseModel):
    proj_folder: str = ''
    description_model: str = 'gpt-3.5-turbo-1106'
    chat_model: str = 'gpt-4-1106-preview'
    default_project_include: list[str] = ['README.md', 'package.json']
    default_project_exclude: list[str] = []
    default_project_gitignore: bool = True
    default_project_remove_comments: bool = False
    verbose_log: bool = False

