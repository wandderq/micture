import logging as lg
from pathlib import Path

import numpy as np
from PIL import Image

from yamig.utils.exceptions import PreprocessorError
from yamig.utils.logging import timeit
from yamig.utils.params import YamigParams


class Preprocessor:
    def __init__(self, params: YamigParams):
        self.logger = lg.getLogger('yamig.preprocessor')
        self.params = params

    @timeit
    def run(self) -> tuple[np.array, np.array]:
        """yamig image preprocessor

        Returns:
            tuple[np.array, np.array]: image array, image palette.
        """
        # load
        self.logger.info(f'loading image: {self.params.input_path}')
        img = Image.open(self.params.input_path).convert('RGB')
        self.logger.debug(f'original image resolution: {img.size}')

        # resize
        self.logger.info(f'resizing image to the target resolution: {self.params.resolution}')
        img = img.resize(self.params.resolution, Image.Resampling.LANCZOS)

        # quantize
        self.logger.info(f'quanting image palette to {self.params.max_colors} colors')
        img = img.quantize(
            colors=self.params.max_colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE
        ).convert('RGB')

        # palette
        self.logger.debug(f'getting image palette')
        img_array = np.array(img, dtype=np.float32)
        img_palette = np.unique(img_array.reshape(-1, 3), axis=0)
        self.logger.debug(f'palette length: {len(img_palette)}')

        # debug
        if self.params.debug_path is not None:
            preprocessed_image_path = self.params.debug_path / 'preprocessed.jpg'
            img.save(preprocessed_image_path)
            self.logger.debug(f'preprocessed image saved to {str(preprocessed_image_path)}')

        return img_array, img_palette