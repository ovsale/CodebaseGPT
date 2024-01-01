from pydantic import BaseModel

class ProjConfig(BaseModel):
    path: str = ''
    include: list[str] = []
    exclude: list[str] = []
    gitignore: bool = False
    remove_comments: bool = False