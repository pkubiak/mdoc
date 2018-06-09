from .renderer import Renderer


class HTMLRenderer(Renderer):
    @staticmethod
    def render_heading(level, text):
        return "<h%d>%s</h%d>\n" % (level, text, level)


    @staticmethod
    def render_paragraph(text):
        return "<p>%s</p>\n\n" % (text, )


    @staticmethod
    def render_widget(name, params, body):
        return '<h3>Widget: %s</h3>\n' % (name, )
