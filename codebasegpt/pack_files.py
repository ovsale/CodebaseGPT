class PackFiles:
    def __init__(self, path: str, files: list[str]):
        self.path = path
        self.files = files

    def __repr__(self):
        return f'PackFiles(path={self.path}, files={self.files})'