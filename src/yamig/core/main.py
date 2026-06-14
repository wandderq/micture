import logging as lg
from dataclasses import asdict
from pprint import pformat

from yamig import __version__
from yamig.core.mlog import MlogGenerator
from yamig.core.preprocessor import Preprocessor
from yamig.core.quadtree import QuadtreeProcessor
from yamig.core.schema import SchemaGenerator
from yamig.utils.params import YamigParams


class Yamig:
    def __init__(self, params: YamigParams) -> None:
        self.logger = lg.getLogger("yamig.core")
        self.params = params
    
    
    def run(self) -> None:
        self.logger.info("yamig v%s", __version__)
        self.logger.debug(pformat(asdict(self.params)))

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
