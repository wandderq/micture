import logging as lg
import sys
import time
from argparse import Namespace
from collections.abc import Callable
from functools import wraps
from logging import StreamHandler
from typing import ParamSpec, TypeVar

from colorlog import ColoredFormatter


def setup_logger(args: Namespace) -> None:
    level = (
        lg.DEBUG if args.verbose else
        lg.WARNING if args.quiet else
        0 if args.silent else
        lg.INFO
    )

    root_logger = lg.getLogger("yamig")
    root_logger.handlers.clear()
    root_logger.setLevel(lg.DEBUG)
    
    # if not silent
    if level != 0:
        # stream handler
        stream_handler = StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(
            ColoredFormatter(
                fmt="{log_color}{levelname}{reset}:{name} {message}",
                style="{",
                log_colors={
                    "DEBUG": "blue",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red"
                }
            )
        )
        stream_handler.setLevel(level)
        root_logger.addHandler(stream_handler)

P = ParamSpec("P")
R = TypeVar("R")

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
