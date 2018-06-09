class Renderer:
    @classmethod
    def render(cls, tokens):
        output = []
        for token in tokens:
            name, *params = token

            if name in ['EMPTY_LINE', 'MULTILINE_COMMENT', 'SINGLE_LINE_COMMENT']:
                continue

            method = getattr(self, 'render_' + name.lower())
            result = method(*params)
            output.append(result)
        return "".join(result)
