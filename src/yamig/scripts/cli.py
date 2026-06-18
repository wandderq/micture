import logging as lg
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from pymsch import Content

from yamig import __version__
from yamig.core.main import Yamig
from yamig.utils.exceptions import FileExpectedError
from yamig.utils.logging import YamigLogger
from yamig.utils.params import YamigParams

root_logger = YamigLogger()

class YamigCLI:
    def __init__(self) -> None:
        self.argparser = self._init_argparser()
        self.logger = lg.getLogger("yamig.cli")
    
    #TODO: add --display option (for features/all-displays-support)
    #TODO: add --processor option (for features/all-processors-support)
    def _init_argparser(self) -> ArgumentParser:
        argparser = ArgumentParser(
            description=f"yet another mindustry image generator v{__version__}",
            epilog="github: https://github.com/wandderq/yamig"
        )

        log_group = argparser.add_mutually_exclusive_group()
        
        argparser.add_argument(
            "input_path",
            type=Path,
            help="input image path (PNG/JPG)"
        )

        argparser.add_argument(
            "-o", "--output",
            dest="output_path",
            type=Path,
            default=None,
            help="output path (default: derived from input)"
        )

        argparser.add_argument(
            "--debug",
            dest="debug_path",
            type=Path,
            default=None,
            help="debug path (for intermediate files) (default: None)"
        )
        
        argparser.add_argument(
            "-C", "--to-clipboard",
            dest="to_clipboard",
            action="store_true",
            help="copy schematic to clipboard"
        )

        argparser.add_argument(
            "-r", "--resolution",
            dest="resolution",
            type=str,
            default="300x300px",
            help=(
                "target resolution "
                "(format: WxH[px/d]) "
                "(px - pixels, d - displays) "
                "(default: 300x300px)"
            )
        )

        argparser.add_argument(
            "-c", "--max-colors",
            dest="max_colors",
            type=int,
            default=64,
            help="max image colors (default: 64) (1-255) (up to 15%% loss)"
        )

        argparser.add_argument(
            "-t", "--dispersion-threshold",
            dest="dispersion_threshold",
            type=int,
            default=600,
            help="quadtree color dispersion threshold (default: 600) (>0)"
        )

        argparser.add_argument(
            "-s", "--min-region-size",
            dest="min_region_size",
            type=int,
            default=4,
            help="min quadtree region size (px) (default: 4) (>0)"
        )

        argparser.add_argument(
            "-l", "--max-script-len",
            dest="max_script_len",
            type=int,
            default=1000,
            help="max lines per processor script (default: 1000) (3-1000)"
        )

        argparser.add_argument(
            "-N", "--schema-name",
            dest="schema_name",
            type=str,
            default=None,
            help="schematic name (default: derived from input)"
        )

        argparser.add_argument(
            "-D", "--schema-description",
            dest="schema_description",
            type=str,
            default=None,
            help="schematic description (default: derived from input)"
        )

        argparser.add_argument(
            "-y", "--yes",
            dest="yes",
            action="store_true",
            help="yes"
        )
    
        log_group.add_argument(
            "-v", "--verbose",
            dest="verbose",
            action="store_true",
            help="verbose mode (debug logs)"
        )

        log_group.add_argument(
            "-q", "--quiet",
            dest="quiet",
            action="store_true",
            help="quiet mode (warnings/errors only)"
        )

        log_group.add_argument(
            "--silent",
            dest="silent",
            action="store_true",
            help="silent mode (no logs)"
        )

        return argparser
    

    def _parse_output_path(self, args: Namespace) -> None:
        if args.output_path is None:
            args.output_path = Path(f"{args.input_path.stem}.msch").absolute()
        
        if args.output_path.exists():
            if not args.output_path.is_file():
                raise FileExpectedError(args.output_path)

            warning_msg = f"{args.output_path.name} already exists! Overwrite it? (Y/n) "
            overwrite = (
                True if args.yes
                else input(warning_msg).strip().lower() == "y"
            )

            if overwrite:
                args.output_path.unlink()
            
            else:
                raise FileExistsError(args.output_path)


    def _parse_resolution(self, args: Namespace) -> None:
        match = re.match(r"^(\d+)x(\d+)(px|d)$", args.resolution)
        if not match:
            raise ValueError(args.resolution)
        
        width = int(match.group(1))
        height = int(match.group(2))
        suffix = match.group(3)
        

        if suffix == "px":
            args.resolution = (width, height)
        
        else:
            args.resolution = (width * 32, height * 32)
        #TODO: use actual display size (for features/all-displays-support)


    def run(self) -> None:
        # parse args
        args = self.argparser.parse_args()

        # configure root logger
        root_logger.set_level(
            lg.DEBUG if args.verbose else
            lg.WARNING if args.quiet else
            lg.CRITICAL+1 if args.silent else
            lg.INFO
        )
        root_logger.add_file_handler(args.debug_path)


        # parse args (more)
        self._parse_output_path(args)
        self._parse_resolution(args)

        # params
        params = YamigParams(
            input_path=args.input_path,
            output_path=args.output_path,
            debug_path=args.debug_path,
            to_clipboard=args.to_clipboard,
            resolution=args.resolution,
            max_colors=args.max_colors,
            dispersion_threshold=args.dispersion_threshold,
            min_region_size=args.min_region_size,
            display=Content.TILE_LOGIC_DISPLAY, #TODO: replace it in features/all-displays-support
            processor=Content.MICRO_PROCESSOR, #TODO: replace it in features/all-processors-support
            max_script_len=args.max_script_len,
            schema_name=args.schema_name,
            schema_description=args.schema_description
        )

        # yamig
        Yamig(params).run()


def run_cli() -> None:
    try:
        app = YamigCLI()
        app.run()
        sys.exit(0)
    
    except Exception:
        root_logger.logger.exception()
        sys.exit(1)
    
    except KeyboardInterrupt:
        root_logger.logger.info("interrupted")
        sys.exit(0)


if __name__ == "__main__":
    run_cli()
