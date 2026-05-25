from argparse import ArgumentParser
from pathlib import Path

from yamig.core.main import Yamig
from yamig import __version__

import sys
import re

class YamigCLI:
    def __init__(self):
        self.argparser = self._init_argparser()
    

    def _init_argparser(self) -> ArgumentParser:
        argparser = ArgumentParser(
            description=f'yet another mindustry image generator v{__version__}',
            epilog='github: https://github.com/wandderq/yamig'
        )

        log_group = argparser.add_mutually_exclusive_group()
        
        argparser.add_argument(
            'input_path',
            type=Path,
            help='input image path'
        )

        argparser.add_argument(
            '-o', '--output',
            type=Path,
            default=None,
            dest='output_path',
            help='output directory (default: derived from args)'
        )

        argparser.add_argument(
            '-O', '--onefile',
            dest='onefile',
            action='store_true',
            help='save only .msch file'
        )
        
        argparser.add_argument(
            '-C', '--copy-to-clipboard',
            dest='copy_to_clipboard',
            action='store_true',
            help='copy schematic to clipboard'
        )

        argparser.add_argument(
            '-r', '--resolution',
            type=str,
            default='5x5b',
            dest='resolution',
            help='target resolution (format: WxH[b/px]) (default: 5x5b)'
        )

        argparser.add_argument(
            '-c', '--max-colors',
            type=int,
            default=64,
            dest='max_colors',
            help='max target image colors (default: 64) (up to 15%% loss)'
        )

        argparser.add_argument(
            '-t', '--dispersion-threshold',
            type=int,
            default=600,
            dest='dispersion_threshold',
            help='quadtree color dispersion threshold (default: 600)'
        )

        argparser.add_argument(
            '-s', '--min-region-size',
            type=int,
            default=8,
            dest='min_region_size',
            help='min quadtree region size (px) (default: 8)'
        )

        argparser.add_argument(
            '-l', '--max-script-len',
            type=int,
            default=1000,
            dest='max_script_len',
            help='max lines of script in each processor (default: 100)'
        )

        argparser.add_argument(
            '-N', '--schema-name',
            type=str,
            default=None,
            dest='schema_name',
            help='schematic name (default: derived from args)'
        )

        argparser.add_argument(
            '-D', '--schema-desc',
            type=str,
            default=None,
            dest='schema_desc',
            help='schematic description (default: derived from args)'
        )
    
        log_group.add_argument(
            '-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='verbose mode (debug logs)'
        )

        log_group.add_argument(
            '-q', '--quiet',
            dest='quiet',
            action='store_true',
            help='quiet mode (warn/err logs)'
        )

        log_group.add_argument(
            '--silent',
            dest='silent',
            action='store_true',
            help='silent mode (no logs)'
        )

        return argparser
    

    def _parse_input_path(self, input_path: Path) -> Path:
        input_path = input_path.absolute()

        if not input_path.exists():
            raise FileNotFoundError(f'{str(input_path)} not found!')
        
        if not input_path.is_file():
            raise FileNotFoundError(f'{str(input_path)} is dir!')
        
        return input_path
    

    def _parse_output_path(self, output_path: Path | None, input_path: Path) -> Path:
        if output_path is None:
            output_path = Path(f'yamig_{input_path.stem}').absolute()
        
        else:
            output_path = output_path.absolute()
        
        if output_path.is_file():
            raise FileExistsError(f'{output_path} is file! (should be dir)')
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        return output_path


    def _parse_resolution(self, resolution: str) -> tuple[int, int]:
        match = re.match(r'^(\d+)x(\d+)(px|b)$', resolution)
        if not match:
            raise ValueError(f'Invalid resolution: {resolution}')
        
        width = int(match.group(1))
        height = int(match.group(2))
        suffix = match.group(3)
        

        if suffix == 'px':
            resolution = (
                (width + 16) // 32 * 32,
                (height + 16) // 32 * 32
            )
        
        else:
            resolution = (width * 32, height * 32)
        
        return resolution

    
    def _parse_max_colors(self, max_colors: int) -> int:
        if not (1 <= max_colors <= 256):
            raise ValueError(f'Invalid max colors value: {max_colors} (must be 1-256)')
        
        return max_colors
    
    
    def _parse_dispersion_threshold(self, dispersion_threshold: int) -> int:
        if not (0 <= dispersion_threshold <= 10000):
            raise ValueError(
                f'Invalid color dispersion threshold value: {dispersion_threshold} '
                '(must be 0-10000)'
            )
        
        return dispersion_threshold


    def _parse_min_region_size(self, min_region_size: int) -> int:
        if min_region_size <= 0:
            raise ValueError(
                f'Invalid min region size value: {min_region_size} '
                '(must be > 0)'
            )
        
        return min_region_size
    

    def _parse_max_script_len(self, max_script_len: int) -> int:
        if not (3 <= max_script_len <= 1000):
            raise ValueError(
                f'Invalid max script length value: {max_script_len} '
                '(must be 3-1000)'
            )
        
        return max_script_len
    

    def _parse_schema_name(self,
        schema_name: str | None,
        input_path: Path,
        resolution: tuple[int, int]
    ) -> str:
        if schema_name is None:
            resolution_str = f'{resolution[0]}x{resolution[1]}'
            schema_name = f'{input_path.stem} {resolution_str}'
        
        return schema_name
    

    def _parse_schema_desc(self,
        schema_desc: str | None,
        input_path: Path,
        resolution: tuple[int, int],
        dispersion_threshold: int,
        max_colors: int,
        min_region_size: int
    ) -> str:
        if schema_desc is None:
            resolution_str = f'{resolution[0]}x{resolution[1]}'
            schema_desc = (
                f"{input_path.name} {resolution_str}\n"
                f"max colors: {max_colors}\n"
                f"dispersion threshold: {dispersion_threshold}\n"
                f"min region size: {min_region_size}"
            )
        
        return schema_desc


    def run(self) -> None:
        args = self.argparser.parse_args()

        args.input_path = self._parse_input_path(args.input_path)
        args.output_path = self._parse_output_path(args.output_path, args.input_path)
        args.resolution = self._parse_resolution(args.resolution)
        args.max_colors = self._parse_max_colors(args.max_colors)
        args.dispersion_threshold = self._parse_dispersion_threshold(args.dispersion_threshold)
        args.min_region_size = self._parse_min_region_size(args.min_region_size)
        args.max_script_len = self._parse_max_script_len(args.max_script_len)
        args.schema_name = self._parse_schema_name(
            args.schema_name,
            args.input_path,
            args.resolution
        )
        args.schema_desc = self._parse_schema_desc(
            args.schema_desc,
            args.input_path,
            args.resolution,
            args.dispersion_threshold,
            args.max_colors,
            args.min_region_size
        )

        yamig = Yamig(args)
        yamig.run()


def run_cli() -> None:
    try:
        app = YamigCLI()
        app.run()
        sys.exit(0)
    
    except Exception as e:
        print(f'\033[31m{e.__class__.__name__}: {str(e)}.' + (f' Cause: {e.__cause__}\033[0m' if e.__cause__ else '\033[0m'))
        sys.exit(1)


if __name__ == '__main__':
    run_cli()