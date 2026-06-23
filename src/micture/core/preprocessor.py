import logging as lg

import numpy as np
from PIL import Image

from micture.utils.logging import timeit
from micture.utils.params import Params


class Preprocessor:
    def __init__(self, params: Params) -> None:
        """image loader & preprocessor

        Args:
            params (Params): parameters
        """
        self.logger = lg.getLogger("micture.preprocessor")
        self.params = params

    @timeit
    def run(self) -> tuple[np.array, np.array]:
        """run preprocessor

        Returns:
            tuple[np.array, np.array]: image array, image palette.
        """
        # load
        self.logger.info("loading image %s", self.params.input_path)
        img = Image.open(self.params.input_path).convert("RGB")
        self.logger.debug("original image resolution: %s", img.size)

        # resize
        self.logger.info("resizing image to the target resolution: %s", self.params.resolution)
        img = img.resize(self.params.resolution, Image.Resampling.LANCZOS)

        # quantize
        self.logger.info("quanting image palette to %d colors", self.params.max_colors)
        img = img.quantize(
            colors=self.params.max_colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE
        ).convert("RGB")

        # palette
        self.logger.debug("getting image palette")
        img_array = np.array(img, dtype=np.float32)
        img_palette = np.unique(img_array.reshape(-1, 3), axis=0)
        self.logger.debug("palette length: %d", len(img_palette))

        # debug
        if self.params.debug_path is not None:
            preprocessed_image_path = self.params.debug_path / "preprocessed.jpg"
            img.save(preprocessed_image_path)
            self.logger.debug("preprocessed image saved to %s", preprocessed_image_path)

        return img_array, img_palette

