
class Tool:
    def __init__(self, name, description, function, input_schema, output_schema):
        self.name = name
        self.description = description
        self.function = function
        self.input_schema = input_schema
        self.output_schema = output_schema

    def execute(self, **kwargs):
        return self.function(**kwargs)