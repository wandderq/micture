import json
import logging as lg
import os
from argparse import Namespace

import numpy as np
from PIL import Image
from pymsch import Schematic

from yamig import __version__
from yamig.core.mlog import MlogGenerator
from yamig.core.preprocessor import Preprocessor
from yamig.core.quadtree import QuadtreeProcessor
from yamig.core.schema import SchemaGenerator
from yamig.utils.logging import setup_logger


class Yamig:
    def __init__(self, args: Namespace):
        setup_logger(
            lg.DEBUG if args.verbose
            else lg.WARNING if args.quiet
            else 0 if args.silent
            else lg.INFO,

            (args.output_path / 'yamig.log') if not args.onefile else None
        )
        self.logger = lg.getLogger('yamig')
        self.args = args
    
    
    def run(self) -> None:
        self.logger.info(f'yamig v{__version__}')
        self.logger.debug(f'args: {self.args}')

        image, palette = self._run_preprocessor()
        rects = self._run_quadtree(image, palette)
        scripts = self._run_mlog_generator(rects)
        self._run_schema_generator(scripts)
    

    def _run_preprocessor(self) -> tuple[Image, np.array]:
        self.logger.info('starting preprocessor')
        preprocessor = Preprocessor(
            self.args.input_path,
            self.args.resolution,
            self.args.max_colors
        )
        image, palette = preprocessor.run()

        if not self.args.onefile:
            preprocessed_image_path = self.args.output_path / 'preprocessed.jpg'
            image.save(preprocessed_image_path)
            self.logger.info(f'preprocessed image saved to {str(preprocessed_image_path)}')
        
        return image, palette
    

    def _run_quadtree(self, image: Image, palette: np.array) -> list:
        self.logger.info('starting quadtree')
        quadtree = QuadtreeProcessor(
            image,
            self.args.min_region_size,
            self.args.dispersion_threshold,
            self.args.resolution,
            palette
        )
        rects = quadtree.get_rects()

        if not self.args.onefile:
            rects_json_path = self.args.output_path / 'rects.json'
            with rects_json_path.open(mode='w') as file:
                json.dump(rects, file, indent=2)
            self.logger.info(f'rects saved to {str(rects_json_path)}')

            recomposed_image = quadtree.recompose(rects)
            recomposed_image_path = self.args.output_path / 'recomposed.jpg'
            recomposed_image.save(recomposed_image_path)
            self.logger.info(f'recomposed image saved to {str(recomposed_image_path)}')
        
        return rects

    
    def _run_mlog_generator(self, rects: list) -> list:
        self.logger.info('starting mlog generator')
        mlog_generator = MlogGenerator(
            self.args.max_script_len,
            self.args.resolution
        )
        scripts = mlog_generator.generate_mlog(rects)

        if not self.args.onefile:
            scripts_path = self.args.output_path / 'scripts'
            scripts_path.mkdir(exist_ok=True)

            for script_path in scripts_path.iterdir():
                if script_path.is_file() and script_path.suffix == '.mlog':
                    os.remove(script_path)
            
            for script_i, script in enumerate(scripts, start=1):
                script_path = scripts_path / f'script_{script_i}.mlog'
                self.logger.info(f'saving script {script_path.name}')
                with script_path.open(mode='w') as file:
                    file.write('\n'.join(script))
        
        return scripts
    

    def _run_schema_generator(self, scripts: list) -> Schematic:
        schema_generator = SchemaGenerator(
            scripts,
            self.args.resolution,
            self.args.schema_name,
            self.args.schema_desc
        )

        schema = schema_generator.generate_schema()

        schema_path = self.args.output_path / (self.args.schema_name + '.msch')
        schema.write_file(schema_path)
        self.logger.info(f'schema saved to {str(schema_path)}')

        if self.args.copy_to_clipboard:
            schema.write_clipboard()