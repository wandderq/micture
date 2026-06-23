# micture - mindustry picture
Converts pictures to mindustry logic schematics


## Features
- works only with **tile displays** and **micro processors** (all processors & displays support soon)
- fully customizable schematic generation:
  - image resolution & scaling
  - color quantization limits
  - quadtree optimization parameters
  - schematic metadata (name, description)
  - output format options


## Installation
Python 3.12 or higher is required.

### Using pip/pipx
```bash
pipx install git+https://github.com/wandderq/micture.git
```

### From source
```bash
git clone https://github.com/wandderq/micture
cd micture
pip install .
```

## Dependencies
- `pillow` - image processing
- `numpy` - array operations
- `pymsch` - schematic generating


## Usage

### Positional arguments
| argument | description |
|----------|-------------|
|`input_path`|input image path (PNG/JPG)|

### Options
| option | description |
|--------|-------------|
|`-h, --help`|show help message|
|`-o, --output`|output path (default: derived from input)|
|`--debug`|debug path (for intermediate files) (default: None)|
|`-C, --to-clipboard`|copy schematic to clipboard|
|`-r, --resolution`|target resolution (format: `WxH[px/d]`) (px - pixels, d - displays) (default: `300x300px`)|
|`-c, --max-colors`|max image colors (default: `64`) (1-255) (up to 15% loss)|
|`-d, --dispersion-threshold`|quadtree color dispersion threshold (default: `600`) (>0)|
|`-s, --min-region-size`|min quadtree region size (px) (default: `4`) (>0)|
|`-l, --max-script-len`|max lines per processor script (default: `1000`) (3-1000)|
|`-N, --schema-name`|schematic name (default: derived from input)|
|`-D, --schema-description`|schematic description (default: derived from input)|
|`-y, --yes`|yes|
|`-v, --verbose`|verbose mode (debug logs)|
|`-q, --quiet`|quiet mode (warnings/errors only)|
|`--silent`|silent mode (no logs)|


## Examples
1. basic usage
```bash
micture picture.jpg
```
2. custom resolution and output path
```bash
micture picture.jpg -r 10x10d -o schematics/pic_10x10d.msch
```
3. higher quality
```bash
micture picture.jpg -r 16x9d -c 256 -s 2 -d 200
```
4. accelerated in-game rendering (but more processors)
```bash
micture picture.jpg -r 800x600px -c 256 -s 1 -l 300
```

## License
Distributed under [MIT License](https://github.com/wandderq/micture/blob/main/LICENSE) - free to use, modify, and distribute
