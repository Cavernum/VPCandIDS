import logging
from rich.logging import RichHandler
from rich.console import Console

def enable():
    debug_console = Console(tab_size=4, stderr=True)

    logging.basicConfig(
            level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(console=debug_console, rich_tracebacks=True)]
            )
