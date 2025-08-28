class BaseUtils:
    END = "\033[m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"

    LIGTH = "\033[1m"
    DARK = "\033[2m"
    ITALIC = "\033[3m"

    WARNING = f"{LIGTH}{YELLOW}[WARNING]{END}"
    ERROR = f"{LIGTH}{RED}[ERROR]{END}"
    INFO = f"{LIGTH}{CYAN}[INFO]{END}"
    MODE = f"{LIGTH}{CYAN}[MODE]{END}"
    REMOVE = f"{LIGTH}{PURPLE}[REMOVE]{END}"
