import json
import logging as lg

import numpy as np
from PIL import Image, ImageDraw

from yamig.utils.logging import timeit
from yamig.utils.params import YamigParams


class QuadtreeProcessor:
    def __init__(self,
        image_array: np.array,
        image_palette: np.array,
        params: YamigParams
    ):
        self.logger = lg.getLogger('yamig.quadtree')
        self.image_array = image_array
        self.image_palette = image_palette
        self.params = params
    
    @timeit
    def run(self) -> list:
        self.logger.info('processing quadtree')
        rects = [
            (r[0], r[1], r[2], r[3], tuple(int(c) for c in r[4]))
            for r in self.decompose(0, 0, *self.params.resolution)
        ]

        if self.params.debug_path is not None:
            image_rects_path = self.params.debug_path / 'quadtree_rects.json'
            recomposed_image_path = self.params.debug_path / 'quadtree_recomposed.jpg'

            # rects.json
            with image_rects_path.open(mode='w') as rects_file:
                json.dump(rects, rects_file, indent=2)
            
            self.logger.debug(f'image rects saved to {str(image_rects_path)}')

            # recomposed.json
            recomposed_image = self.recompose(rects)
            recomposed_image.save(recomposed_image_path)

            self.logger.debug(f'recomposed image saved to {str(recomposed_image_path)}')
        
        return rects
    
    
    def decompose(self, x: int, y: int, w: int, h: int) -> list:
        region = self.image_array[y:y+h, x:x+w]
        region_mean_color = np.mean(region, axis=(0, 1))
        region_color_diff = region.astype(np.float32) - region_mean_color.astype(np.float32)
        region_dispersion = np.mean(np.sum(region_color_diff**2, axis=2))
        
        rects = []

        if (w <= self.params.min_region_size
            or h <= self.params.min_region_size
            or region_dispersion <= self.params.dispersion_threshold
        ):
            rect_color = self._find_closest_color(region_mean_color)
            rects.append((x, y, w, h, rect_color))
        
        else:
            half_w = w // 2
            half_h = h // 2
            rects.extend(self.decompose(x, y, half_w, half_h))
            rects.extend(self.decompose(x + half_w, y, w - half_w, half_h))
            rects.extend(self.decompose(x, y + half_h, half_w, h - half_h))
            rects.extend(self.decompose(x + half_w, y + half_h, w - half_w, h - half_h))
        
        return rects
    

    def recompose(self, rects: list) -> Image:
        image = Image.new('RGB', self.params.resolution, (0, 0, 0))
        draw = ImageDraw.Draw(image)

        for rect in rects:
            x, y, w, h, color = rect
            
            x2 = x + w
            y2 = y + h
            
            draw.rectangle([x, y, x2, y2], fill=color)
        
        return image
    

    def _find_closest_color(self, color):
        distances = np.sum((self.image_palette - color) ** 2, axis=1)
        idx = np.argmin(distances)
        color = tuple(self.image_palette[idx])
        return color