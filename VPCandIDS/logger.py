import logging
from rich.logging import RichHandler
from rich.console import Console

def enable(*, log_level:str = "INFO"):
    debug_console = Console(tab_size=2, stderr=True)

    handler = RichHandler(console=debug_console, rich_tracebacks=True, level=log_level)

    logging.basicConfig(
        level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[handler], force=True
    )
