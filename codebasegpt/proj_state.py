from pydantic import BaseModel


class FileState(BaseModel):
    path: str = ''
    mtime: int = 0
    desc: str = ''
    embed: list[float] = []


class ProjState(BaseModel):
    remove_comments: bool = False
    files: list[FileState] = []
