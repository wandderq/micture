import logging as lg
from dataclasses import asdict
from pprint import pformat

from micture import __version__
from micture.core.mlog import MlogGenerator
from micture.core.preprocessor import Preprocessor
from micture.core.quadtree import Quadtree
from micture.core.schema import SchemaGenerator
from micture.utils.params import Params


class Micture:
    def __init__(self, params: Params) -> None:
        """picture to mindustry schematic converter

        Args:
            params (Params): generator parameters
        """
        self.logger = lg.getLogger("micture.core")
        self.params = params
    
    
    def run(self) -> None:
        """run micture"""
        self.logger.info("micture v%s", __version__)
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
