import logging as lg

from pymsch import Block, Content, ProcessorConfig, ProcessorLink, Schematic

from micture.utils.logging import timeit
from micture.utils.params import Params


class SchemaGenerator:
    def __init__(self, scripts: list, params: Params) -> None:
        """generates mindustry schematic using processors' scripts
        thanks to SkyeTheFoxyFox for the pymsch library

        Args:
            scripts (list): processors' scripts
            params (Params): parameters
        """
        self.logger = lg.getLogger("micture.schema")
        self.scripts = scripts
        self.params = params
    

    @timeit
    def run(self) -> Schematic:
        """run schema generator

        Returns:
            Schematic: schematic
        """
        self.logger.info("generating schema")

        schema = Schematic()
        schema.set_tag("name", self.params.schema_name)

        if self.params.schema_description is not None:
            schema.set_tag("description", self.params.schema_description)
        
        self.add_displays(schema)
        self.add_processors(schema)

        schema.write_file(self.params.output_path)
        self.logger.info("schema saved to %s", self.params.output_path)

        if self.params.to_clipboard:
            self.logger.info("writing schema to clipboard")
            schema.write_clipboard()

        return schema
        
    
    def add_displays(self, schema: Schematic) -> None:
        """add logic displays to the scheamtic
        only supports tile-logic-display

        Args:
            schema (Schematic): schematic
        """
        self.logger.debug("adding displays to schema")
        display_x = self.params.resolution[0] // 32
        display_y = self.params.resolution[1] // 32

        for y in range(display_y):
            for x in range(display_x):
                schema.add_block(Block(Content.TILE_LOGIC_DISPLAY, x, y, None, 0))
    

    def add_processors(self, schema: Schematic) -> None:
        """add processors to the schematic
        only supports micro-processor and tile-logic-display

        Args:
            schema (Schematic): schematic
        """
        self.logger.debug("adding processors to schema")
        max_cols = self.params.resolution[0] // 32

        for script_i, script in enumerate(self.scripts):
            row = script_i // max_cols
            col = script_i % max_cols

            proc_x = col
            proc_y = -1 - row

            link_x, link_y = 0, 0 - proc_y

            link = ProcessorLink(link_x, link_y, "display")
            config = ProcessorConfig("\n".join(script), [link])
            schema.add_block(Block(Content.MICRO_PROCESSOR, proc_x, proc_y, config, 0))
