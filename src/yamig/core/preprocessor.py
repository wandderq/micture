from PIL import Image
from pathlib import Path

import logging as lg
import numpy as np


class PreprocessorError(Exception):
    pass


class Preprocessor:
    def __init__(self, 
        input_path: Path,
        target_resolution: tuple[int,int],
        max_colors: int
    ):
        self.logger = lg.getLogger('amig')

        self.input_path = input_path
        self.target_resolution = target_resolution
        self.max_colors = max_colors
    

    def _calculate_colors(self, img: Image):
        self.logger.info('calculating approximate value of unique colors in image')
        try:
            small_img = img.resize((320, 180), Image.Resampling.NEAREST)
            small_arr = np.array(small_img)

            unique_colors = len(
                np.unique(
                    small_arr.reshape(-1, small_arr.shape[-1]),
                    axis=0
                )
            )
        
        except Exception as e:
            raise PreprocessorError(
                'failed to calculate the approximate'
                f'value of unique colors due to error: {str(e)}'
            ) from e
        
        return unique_colors


    def run(self) -> Image:
        self.logger.info(f'loading image: {self.input_path}')
        img = Image.open(self.input_path).convert('RGB')
        
        self.logger.debug(f'original image resolution: {img.size}')

        colors_before = self._calculate_colors(img)
        self.logger.debug(f'approximate value of colors (original): {colors_before}')
        
        self.logger.info(f'quanting palette to {self.max_colors} colors')
        img = img.quantize(
            colors=self.max_colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE
        ).convert('RGB')

        colors_after = self._calculate_colors(img)
        self.logger.debug(f'approximate value of coors (after): {colors_after}')

        self.logger.info(f'resizing image to the target resolution: {self.target_resolution}')
        img = img.resize(self.target_resolution, Image.Resampling.LANCZOS)

        return img