from pathlib import Path
from colorlog import ColoredFormatter
from logging import Formatter, StreamHandler, FileHandler

import logging as lg
import sys


def setup_logger(level: int, log_filepath: Path | None):
    root_logger = lg.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(lg.DEBUG if level != 0 else 100)
    
    # if not silent
    if level != 0:
        # stream handler
        stream_handler = StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(
            ColoredFormatter(
                fmt="{log_color}{levelname}{reset}:{name} {message}",
                style='{',
                log_colors={
                    'DEBUG': 'blue',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red'
                }
            )
        )
        stream_handler.setLevel(level)
        root_logger.addHandler(stream_handler)

        # file_handler
        if log_filepath is not None:
            file_handler = FileHandler(
                filename=log_filepath,
                mode='w',
                encoding='utf-8'
            )
            file_handler.setFormatter(
                Formatter(
                    fmt="{asctime} {name} {levelname}: {message}",
                    style='{',
                    datefmt="%Y.%m.%d-%H:%M:%S"
                )
            )
            file_handler.setLevel(lg.DEBUG)
            root_logger.addHandler(file_handler)

        
