from pymsch import Content

DISPLAYS = {
    "tile": Content.TILE_LOGIC_DISPLAY,
    "normal": Content.LOGIC_DISPLAY,
    "large": Content.LARGE_LOGIC_DISPLAY,
}

PROCESSORS = {
    "micro": Content.MICRO_PROCESSOR,
    "logic": Content.LOGIC_PROCESSOR,
    "hyper": Content.HYPER_PROCESSOR,
}

DISPLAY_RESOLUTIONS = {
    Content.TILE_LOGIC_DISPLAY: 32,
    Content.LOGIC_DISPLAY: 80,
    Content.LARGE_LOGIC_DISPLAY: 176,
}
