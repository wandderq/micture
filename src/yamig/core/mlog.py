import copy
import logging as lg
import os

from yamig.utils.logging import timeit
from yamig.utils.params import YamigParams


class MlogGenerator:
    def __init__(self, image_rects: list, params: YamigParams):
        self.logger = lg.getLogger('yamig.mlog-generator')
        self.image_rects = image_rects
        self.params = params

    @timeit
    def run(self) -> list[str]:
        rects = self.flip_coords(self.image_rects)
        color2rects = self.sort_rects_by_color(rects)
        big_script = self.generate_big_script(color2rects)
        scripts = self.split_big_script(big_script)

        if self.params.debug_path is not None:
            scripts_path = self.params.debug_path / 'scripts/'
            scripts_path.mkdir(exist_ok=True)

            # remove existing scripts
            for script_path in scripts_path.iterdir():
                if script_path.is_file() and script_path.suffix == '.mlog':
                    self.logger.debug(f'removing old script: {str(script_path)}')
                    os.remove(script_path)
            
            # save scripts
            for i, script in enumerate(scripts, start=1):
                script_path = scripts_path / f"script{i}.mlog"
                with script_path.open(mode='w') as file:
                    file.write('\n'.join(script) + '\n')
                
                self.logger.debug(f'script {i} saved to {str(script_path)}')

        return scripts
    

    def flip_coords(self, rects: list) -> list:
        flipped_rects = []

        for rect in rects:
            x, y, w, h, color = rect

            flipped_rect = [x, self.params.resolution[1]-y-h, w, h, color]
            flipped_rects.append(flipped_rect)

        return flipped_rects
    

    def sort_rects_by_color(self, rects: list) -> dict[tuple, list]:
        self.logger.debug('sorting rects by color')
        color2rects = {}

        for rect in rects:
            color = rect[4]

            if color not in color2rects:
                color2rects[color] = []
            
            color2rects[color].append(rect[:4])
        
        self.logger.debug(f'total rect colors: {len(color2rects)}')
        return color2rects
    

    def generate_big_script(self, color2rects: dict):
        self.logger.debug('generating big script')
        script = []

        for color, rects in color2rects.items():
            script.append(f'draw color {color[0]} {color[1]} {color[2]} 255')
            script.extend([
                f'draw rect {r[0]} {r[1]} {r[2]} {r[3]}'
                for r in rects
            ])
        
        self.logger.debug(f'big script length: {len(script)}')
        
        return script
    

    def split_big_script(self, big_script: str) -> list[str]:
        scripts = []
        script = []

        current_color = None

        for line_i, line in enumerate(big_script, start=1):
            if line.startswith('draw color'):
                current_color = line
                
                if line_i != 1:
                    script.append(f'drawflush display1')
                script.append(line)
                continue

            if len(script) % (self.params.max_script_len-1) == 0:
                script.append(f'drawflush display1')
                self.logger.debug(f'adding script part len={len(script)}')
                scripts.append(copy.deepcopy(script))
                script = [current_color]
                continue

            script.append(line)
        
        self.logger.debug(f'adding script part len={len(script)}')
        script.append(f'drawflush display1')
        scripts.append(copy.deepcopy(script))

        return scripts
