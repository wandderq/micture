from argparse import ArgumentParser
from pathlib import Path
from colorlog import ColoredFormatter

from yamig.core.preprocessor import Preprocessor

import logging as lg
import sys


class amigcli:
    def __init__(self):
        self.argparser = self._init_argparser()
    

    def _init_argparser(self) -> ArgumentParser:
        argparser = ArgumentParser(
            description='yet another mindustry image generator'
        )

        argparser.add_argument(
            'input-path',
            type=Path,
            help='input image filepath'
        )

        argparser.add_argument(
            '-o', '--output-path',
            type=Path,
            default=None,
            help='output directory (default: derived from input_path)'
        )

        argparser.add_argument(
            '-r', '--target-resolution',
            default='320x180',
            type=str,
            help='target resolution (default: 320x180)'
        )

        argparser.add_argument(
            '-c', '--max-colors',
            default=64,
            type=int,
            help='max colors in the target image (default: 64)'
        )

        argparser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='debug logs'
        )

        return argparser
    

    def _setup_logger(self, verbose: bool, log_file_path: Path) -> lg.Logger:
        stream_handler = lg.StreamHandler(stream=sys.stdout)
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

        file_handler = lg.FileHandler(
            filename=log_file_path,
            mode='w',
            encoding='utf-8'
        )
        file_handler.setFormatter(
            lg.Formatter(
                fmt="{asctime} {name} {levelname}: {message}",
                style='{',
                datefmt="%Y.%m.%d-%H:%M:%S"
            )
        )

        lg.basicConfig(
            level=lg.DEBUG if verbose else lg.INFO,
            handlers=[stream_handler, file_handler]
        )

        return lg.getLogger('amig.cli')
    

    def _parse_output_path(self, input_path: Path, output_path: Path | None) -> Path:
        if output_path is None:
            output_name = f'{input_path.stem}_output'
            output_path = Path(output_name).absolute()
        
        else:
            output_path = output_path.absolute()
        
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    

    def _parse_input_path(self, input_path: Path) -> Path:
        if not input_path.exists() or not input_path.is_file():
            raise FileNotFoundError(f'Input file \'{str(input_path)}\' not found!')
        
        return input_path.absolute()
    

    def _parse_target_resolution(self, target_resolution: str) -> tuple[int,int]:
        target_resolution_parts = target_resolution.strip().lower().split('x')
        if len(target_resolution_parts) != 2 or not all(part.isdigit() for part in target_resolution_parts):
            raise ValueError(f'Invalid resolution format: {target_resolution}')
        
        return (int(target_resolution_parts[0]), int(target_resolution_parts[1]))
    
    
    def _parse_max_colors(self, max_colors: int) -> int:
        if max_colors < 2:
            raise ValueError('Max colors value must be at least 2')
        
        return max_colors


    def run_cli(self) -> None:
        args = self.argparser.parse_args()

        # parsing args
        args.input_path = self._parse_input_path(args.input_path)
        args.output_path = self._parse_output_path(args.input_path, args.output_path)
        args.target_resolution = self._parse_target_resolution(args.target_resolution)
        args.max_colors = self._parse_max_colors(args.max_colors)

        # setting up
        logger = self._setup_logger(
            args.verbose,
            args.output_path / 'amig.log'
        )
        preprocessor = Preprocessor(
            args.input_path,
            args.target_resolution,
            args.max_colors
        )

        # processing image
        logger.info('amig started')
        image = preprocessor.run()
        
        preprocessed_image_path = args.output_path / 'preprocessed.jpg'
        logger.debug(f'saving preprocessed image to {str(preprocessed_image_path)}')
        image.save(preprocessed_image_path)

        

def run_cli() -> None:
    amigcli().run_cli()
    sys.exit(0)