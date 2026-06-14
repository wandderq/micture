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
from yamig.utils.params import YamigParams


class Yamig:
    def __init__(self, params: YamigParams):
        self.logger = lg.getLogger('yamig.core')
        self.params = params
    
    
    def run(self) -> None:
        self.logger.info(f'yamig v{__version__}')
        self.logger.debug(f'params: {self.params}')

        # preprocessor
        image_array, image_palette = Preprocessor(self.params).run()

        # quadtree
        image_rects = QuadtreeProcessor(
            image_array,
            image_palette,
            self.params
        ).run()

        # mlog generator
        scripts = MlogGenerator(
            image_rects,
            self.params
        ).run()

        # schema generator
        SchemaGenerator(
            scripts,
            self.params
        ).run()