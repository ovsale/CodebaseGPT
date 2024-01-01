from .app_state import AppState
from .init_logic import do_init
from .desc_logic import do_desc
from .chat_logic import do_chat

def main():
    app_state = AppState()
    cont = do_init(app_state)
    if not cont:
        return
    
    cont = do_desc(app_state)
    if not cont:
        return
    
    do_chat(app_state)


# if __name__ == "__main__":
#     main()
