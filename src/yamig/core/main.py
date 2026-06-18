import logging as lg
from dataclasses import asdict
from pprint import pformat

from yamig import __version__
from yamig.core.mlog import MlogGenerator
from yamig.core.preprocessor import Preprocessor
from yamig.core.quadtree import Quadtree
from yamig.core.schema import SchemaGenerator
from yamig.utils.params import YamigParams


class Yamig:
    def __init__(self, params: YamigParams) -> None:
        """yamig - yet another mindustry image generator
        generates schematics using PNG/JPG files
        this is the core class, should be used by other interfaces like CLI or GUI

        Args:
            params (YamigParams): generator parameters
        """
        self.logger = lg.getLogger("yamig.core")
        self.params = params
    
    
    def run(self) -> None:
        """run yamig"""
        self.logger.info("yamig v%s", __version__)
        self.logger.debug(pformat(asdict(self.params)))

        # preprocessor
        self.logger.info("launching preprocessor")
        image_array, image_palette = Preprocessor(self.params).run()

        # quadtree
        self.logger.info("launching quadtree")
        image_rects = Quadtree(
            image_array,
            image_palette,
            self.params
        ).run()

        # mlog generator
        self.logger.info("launching mlog generator")
        scripts = MlogGenerator(
            image_rects,
            self.params
        ).run()

        # schema generator
        self.logger.info("launching schema generator")
        SchemaGenerator(
            scripts,
            self.params
        ).run()

        # done
        self.logger.info("done!")
