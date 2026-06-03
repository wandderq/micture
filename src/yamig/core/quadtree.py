import logging as lg

import numpy as np
from PIL import Image, ImageDraw


class QuadtreeProcessor:
    def __init__(self,
        image: Image,
        min_region_size: int,
        dispersion_threshold: int,
        resolution: tuple[int,int],
        palette: np.array
    ):
        self.logger = lg.getLogger('yamig.quadtree')
        self.image_array = np.array(image, dtype=np.float32)
        self.min_region_size = min_region_size
        self.dispersion_threshold = dispersion_threshold
        self.resolution = resolution
        self.palette = palette
    

    def _find_closest_color(self, color):
        distances = np.sum((self.palette - color) ** 2, axis=1)
        return np.argmin(distances)


    def decompose(self, x: int, y: int, w: int, h: int) -> list:
        region = self.image_array[y:y+h, x:x+w]
        region_mean_color = np.mean(region, axis=(0, 1))
        region_color_diff = region.astype(np.float32) - region_mean_color.astype(np.float32)
        region_dispersion = np.mean(np.sum(region_color_diff**2, axis=2))
        
        rects = []

        if (w <= self.min_region_size
            or h <= self.min_region_size
            or region_dispersion <= self.dispersion_threshold
        ):
            idx = self._find_closest_color(region_mean_color)
            rect_color = tuple(self.palette[idx])
            rects.append((x, y, w, h, rect_color))
        
        else:
            half_w = w // 2
            half_h = h // 2
            rects.extend(self.decompose(x, y, half_w, half_h))
            rects.extend(self.decompose(x + half_w, y, w - half_w, half_h))
            rects.extend(self.decompose(x, y + half_h, half_w, h - half_h))
            rects.extend(self.decompose(x + half_w, y + half_h, w - half_w, h - half_h))
        
        return rects
    
    
    def get_rects(self) -> list:
        rects = self.decompose(0, 0, *self.resolution)
        return [
            (r[0], r[1], r[2], r[3], tuple(int(c) for c in r[4]))
            for r in rects
        ]
    

    def recompose(self, rects: list) -> Image:
        self.logger.debug('recomposing image from rects')
        image = Image.new('RGB', self.resolution, (0, 0, 0))
        draw = ImageDraw.Draw(image)

        for rect in rects:
            x, y, w, h, color = rect
            
            x2 = x + w
            y2 = y + h
            
            draw.rectangle([x, y, x2, y2], fill=color)
        
        return image