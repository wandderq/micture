import logging as lg

from pymsch import Block, Content, ProcessorConfig, ProcessorLink, Schematic


class SchemaGenerator:
    def __init__(self,
        scripts: list,
        target_resolution: tuple[int,int],
        schema_name: str,
        schema_description: str,
    ):
        self.logger = lg.getLogger('yamig.schema-generator')
        self.scripts = scripts
        self.target_resolution = target_resolution
        self.schema_name = schema_name
        self.schema_description = schema_description
    

    def generate_schema(self) -> Schematic:
        schema = Schematic()
        schema.set_tag("name", self.schema_name)

        if self.schema_description is not None:
            schema.set_tag("description", self.schema_description)
        
        self.add_displays(schema)
        self.add_processors(schema)

        return schema
        
    
    def add_displays(self, schema: Schematic) -> None:
        display_x = self.target_resolution[0] // 32
        display_y = self.target_resolution[1] // 32

        for y in range(display_y):
            for x in range(display_x):
                schema.add_block(Block(Content.TILE_LOGIC_DISPLAY, x, y, None, 0))
    

    def add_processors(self, schema: Schematic) -> None:
        max_cols = self.target_resolution[0] // 32

        for script_i, script in enumerate(self.scripts):
            row = script_i // max_cols
            col = script_i % max_cols

            proc_x = col
            proc_y = -1 - row

            link_x, link_y = 0, 0 - proc_y

            link = ProcessorLink(link_x, link_y, "display")
            config = ProcessorConfig('\n'.join(script), [link])
            schema.add_block(Block(Content.MICRO_PROCESSOR, proc_x, proc_y, config, 0))