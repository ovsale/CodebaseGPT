from openai import OpenAI
from .app_config import AppConfig
from .proj_config import ProjConfig
from .proj_state import ProjState


class AppState:
    app_config: AppConfig = None
    proj_config: ProjConfig = None
    file_paths: list[str] = []
    proj_state: ProjState = None
    openai: OpenAI = None