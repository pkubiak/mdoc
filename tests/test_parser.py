import unittest, sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from parameterized import parameterized
from mdoc import parser


class ParserTestCase(unittest.TestCase):
    @parameterized.expand([
        # ('name', '/* comment */', ''),
        # ('multline-02', 'hello/* comment */ world', 'hello world'),
        # ('multiline-with-inline', '/* hello // sadad */', ''),
        # ('multiline-with-newline', "4/* Hello \n\n\n\nWordl\n*/2", '42'),
        # ('multiple-multiline', 'H/* 123 */el/*456*/lo Wo/* 789 */rld', 'Hello World'),
        # ('', ";$asd: 'asdas;d'", ...),
        # ('string-may-contain-whitespace', '$x: "   "', '...'),
        # ('string-variable-interpolation', '$x: "#{date}"', '...')
        ('single-line-empty-widget-01', '@image()', [('WIDGET', 'image', {}, None)]),
        ('single-line-empty-widget-02', '@image(     \t)', [('WIDGET', 'image', {}, None)]),
        ('widget-with-param-01', '@image(src="img.jpg")', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),
        ('widget-with-param-02-whitespaces', '@image(  src =   "img.jpg"  )', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),
        ('widget-with-param-03-multiline', '@image(\n\tsrc="img.jpg"\n)', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),

        # ('multi-line-widget', '@image(\nsrc="img.jpg"\n)', [('WIDGET', 'image', {'src': 'img.jpg'}, None)])
        ('single-line-widget-with-params',
         '@image(src="img.jpg", margin=5, border=true)',
         [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True)}, None)]),
        ('multi-line-widget-with-params',
         '@image(\n  src="img.jpg",\n  margin=5,\n  border=true\n)',
         [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True)}, None)]),
        ('widget-with-identifier', '@image(src = $src)', [('WIDGET', 'image', {'src': ('IDENTIFIER', 'src')}, None)])
    ])
    def test_parser(self, name, text, expected):
        self.assertEqual(parser.parse(text), expected, name)




if __name__ == '__main__':
    unittest.main()
