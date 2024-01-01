class ProjStat:
    def __init__(self, file_count: int, total_size: int, large_files: list):
        self.file_count = file_count
        self.total_size = total_size
        self.large_files = large_files

    def __repr__(self):
        return f'ProjStat(file_count={self.file_count}, total_size={self.total_size}, large_files={self.large_files})'