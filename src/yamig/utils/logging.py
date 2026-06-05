import logging as lg
import sys
from argparse import Namespace
from logging import FileHandler, Formatter, StreamHandler
from pathlib import Path

from colorlog import ColoredFormatter


def setup_logger(args: Namespace):
    if args.verbose:
        level = lg.DEBUG
    
    elif args.quiet:
        level = lg.WARNING
    
    elif args.silent:
        level = 0
    
    else:
        level = lg.INFO

    root_logger = lg.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(lg.DEBUG)
    
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
        log_filepath = None if args.onefile else (args.output_path / 'yamig.log')

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

        
