from pydantic import BaseModel

from codebasegpt import app_config

class ProjConfig(BaseModel):
    path: str = ''
    include: list[str] = ['**/*']
    exclude: list[str] = []
    gitignore: bool = True
    remove_comments: bool = False
    desc_mode: str = app_config.MODE_DESC
