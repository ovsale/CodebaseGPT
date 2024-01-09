from pydantic import BaseModel


class FileState(BaseModel):
    path: str = ''
    mtime: int = 0
    desc: str = ''
    desc2: str = ''
    embed: list[float] | None = []


class ProjState(BaseModel):
    remove_comments: bool = False
    files: list[FileState] = []
