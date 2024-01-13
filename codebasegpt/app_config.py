from pydantic import BaseModel


MODE_DESC = "desc"
MODE_DESC_NO = "desc_no"
MODE_DESC_2 = "desc_2"

class AppConfig(BaseModel):
    proj_folder: str = ''
    description_model: str = 'gpt-3.5-turbo-1106'
    embedding_model: str = 'text-embedding-ada-002'
    chat_model: str = 'gpt-4-1106-preview'
    base_url: str = ""
    default_project_include: list[str] = ['**/*']
    default_project_exclude: list[str] = []
    default_project_gitignore: bool = True
    default_project_remove_comments: bool = False
    default_project_desc_mode: str = MODE_DESC
    verbose_log: bool = False

