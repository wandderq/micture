import logging as lg
import sys
import time
from collections.abc import Callable
from functools import wraps
from logging import FileHandler, Formatter, StreamHandler
from pathlib import Path
from typing import ParamSpec, TypeVar

from colorlog import ColoredFormatter

P = ParamSpec("P")
R = TypeVar("R")


class YamigLogger:
    def __init__(self) -> None:
        self.logger = lg.getLogger("yamig")
        self.logger.handlers.clear()
        self.logger.setLevel(lg.DEBUG)

        self.file_handler = None

        self.stream_handler = StreamHandler(stream=sys.stdout)
        self.stream_handler.setFormatter(ColoredFormatter(
            fmt="{name}:{log_color}{levelname}{reset}: {message}",
            style="{",
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red"
            }
        ))
        self.stream_handler.setLevel(lg.INFO)
        self.logger.addHandler(self.stream_handler)


    def set_level(self, level: int) -> None:
        return self.stream_handler.setLevel(level)


    def add_file_handler(self, debug_path: Path | None) -> None:
        if debug_path is None:
            return
        
        self.file_handler = FileHandler(debug_path / "debug.log", mode="w")
        self.file_handler.setLevel(lg.DEBUG)
        self.file_handler.setFormatter(Formatter(
            fmt="{asctime} {name} {levelname}: {message}",
            datefmt="%Y.%m.%d %H:%M:%S",
            style="{"
        ))

        self.logger.addHandler(self.file_handler)



def timeit(func: Callable) -> Callable:
    timeit_logger = lg.getLogger("yamig.timeit")
    qualname = func.__qualname__

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        elapsed_time = end_time - start_time

        timeit_logger.debug("%s took %.4f to execute", qualname, elapsed_time)

        return result
    return wrapper
