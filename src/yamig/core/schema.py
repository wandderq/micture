import logging as lg

from pymsch import Block, Content, ProcessorConfig, ProcessorLink, Schematic

from yamig.utils.logging import timeit
from yamig.utils.params import YamigParams


class SchemaGenerator:
    def __init__(self,
        scripts: list,
        params: YamigParams
    ):
        self.logger = lg.getLogger('yamig.schema-generator')
        self.scripts = scripts
        self.params = params
    

    @timeit
    def run(self) -> Schematic:
        schema = Schematic()
        schema.set_tag("name", self.params.schema_name)

        if self.params.schema_description is not None:
            schema.set_tag("description", self.params.schema_description)
        
        self.add_displays(schema)
        self.add_processors(schema)

        schema.write_file(self.params.output_path)
        self.logger.info(f'schema saved to {str(self.params.output_path)}')

        if self.params.to_clipboard:
            schema.write_clipboard()

        return schema
        
    
    def add_displays(self, schema: Schematic) -> None:
        display_x = self.params.resolution[0] // 32
        display_y = self.params.resolution[1] // 32

        for y in range(display_y):
            for x in range(display_x):
                schema.add_block(Block(Content.TILE_LOGIC_DISPLAY, x, y, None, 0))
    

    def add_processors(self, schema: Schematic) -> None:
        max_cols = self.params.resolution[0] // 32

        for script_i, script in enumerate(self.scripts):
            row = script_i // max_cols
            col = script_i % max_cols

            proc_x = col
            proc_y = -1 - row

            link_x, link_y = 0, 0 - proc_y

            link = ProcessorLink(link_x, link_y, "display")
            config = ProcessorConfig('\n'.join(script), [link])
            schema.add_block(Block(Content.MICRO_PROCESSOR, proc_x, proc_y, config, 0))