import unittest, sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from parameterized import parameterized
from mdoc.parser import tokenize


# class ParserTestCase(unittest.TestCase):
#     @parameterized.expand([
#         # ('name', '/* comment */', ''),
#         # ('multline-02', 'hello/* comment */ world', 'hello world'),
#         # ('multiline-with-inline', '/* hello // sadad */', ''),
#         # ('multiline-with-newline', "4/* Hello \n\n\n\nWordl\n*/2", '42'),
#         # ('multiple-multiline', 'H/* 123 */el/*456*/lo Wo/* 789 */rld', 'Hello World'),
#         # ('', ";$asd: 'asdas;d'", ...),
#         # ('string-may-contain-whitespace', '$x: "   "', '...'),
#         # ('string-variable-interpolation', '$x: "#{date}"', '...')
#         ### COMMENTS ###
#
#         ### VARIABLES ###
#
#         ### WIDGETS ###
#
#         #
#         ('widget-without-params', '%widget', [('WIDGET', 'widget', {}, None)]),
#
#         ('single-line-empty-widget-01', '@image()', [('WIDGET', 'image', {}, None)]),
#
#         ('single-line-empty-widget-02', '@image(     \t)', [('WIDGET', 'image', {}, None)]),
#
#         ('widget-with-param-01', '@image(src="img.jpg")', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),
#
#         ('widget-with-param-02-whitespaces', '@image(  src =   "img.jpg"  )', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),
#
#         ('widget-with-param-03-multiline', '@image(\n\tsrc="img.jpg"\n)', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),
#
#         ('single-line-widget-with-params',
#          '@image(src="img.jpg", margin=5, border=true)',
#          [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True)}, None)]),
#
#         ('multi-line-widget-with-params',
#          '@image(\n  src="img.jpg",\n  margin=5,\n  border=true\n)',
#          [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True)}, None)]),
#
#         ('widget-with-identifier', '@image(src = $src)', [('WIDGET', 'image', {'src': ('IDENTIFIER', 'src')}, None)]),
#         ('widget-with-empty-block', '@image() {\n}', [('WIDGET', 'image', {}, '')]),
#
#         ### PARAGRAPHS ###
#     ])
#     def test_parser(self, name, text, expected):
#         self.assertEqual(parser.parse(text), expected, name)
#
#     def test_01(self):
#         self.assertTokenizer([
#             '%widget'
#         ], [
#             ('WIDGET', '')
#         ])

#
# class TokenizeWidgetTestCase(unittest.TestCase):
#     """
#
#     """
#     def assertTokenize(self, inputs, output):
#         if not all(isinstance(i, list) for i in inputs):
#             inputs = [inputs]
#         for input in inputs:
#             self.assertEqual(tokenize("\n".join(input)), output)
#
#     @parameterized.expand([
#         ('%widget\n', True),
#         ('%widget()\n', True),
#         ('%widget() {\n',
#           '}'])
#
#     ])
#     def test_without_params_and_body(self, input, is_ok):
#         """
#         When widget doesn't have params and body, paranthesis can be omited but they mustn't
#         """
#         output = [('WIDGET', 'widget', {}, None)]
#
#         self.assertTokenize([
#             [
#             '%widget'
#         ], output)
#
#         self.assertTokenize([
#             '%widget()'
#         ], output)
#
#         self.assertTokenize([
#             '%widget() {',
#             '}'
#         ], output)
#
#
#         self.assertSyntaxError([
#             '%widget {}',
#         ])


class TokenizeTestCase(unittest.TestCase):
    @parameterized.expand([
        ### COMMENTS ###

        # Leading and trailing whitespaces are removed from block comment
        ('comments/block_comment_trim', [('BLOCK_COMMENT', 'Line1\nLine2')]),

        # Block comments are parser eager way, from """ to next """
        ('comments/block_comment_eager', SyntaxError),

        # Leading and trailing whitespaces are removed from inline comment
        ('comments/inline_comment_trim', [('INLINE_COMMENT', 'Line1')]),

        # Inline comment can be place next to other tokens, then their token precede them
        ('comments/inline_comment_order', [('INLINE_COMMENT', 'comment next to heading'), ('HEADING', 1, 'heading'), ('INLINE_COMMENT', 'guard')]),

        ### HEADINGS ###

        # Empty line is required after heading
        ('headings/heading_no_empty_line', SyntaxError),

        # Number of oppening '#' must match number of closing '#'
        ('headings/heading_unbalanced', SyntaxError),

        # Three levels of heading are supported
        ('headings/heading_levels', [('HEADING', 1, 'heading1'), ('HEADING', 2, 'heading2'), ('HEADING', 3, 'heading3'), ('INLINE_COMMENT', 'guard')]),
        ('headings/heading_level_4', SyntaxError),

        # Heading text must be surounded with whitespace
        ('headings/heading_not_surrounded', SyntaxError),

        # Whitespace are trimmed from heading text
        ('headings/heading_trim_whitespace', [('HEADING', 1, 'heading1'), ('INLINE_COMMENT', 'guard')]),

        ### VARIABLES ###

        ('variables/correct', [
            ('VARIABLE', 'pi', ('FLOAT', 3.14)),
            ('VARIABLE', 'negative-pi', ('FLOAT', -3.141592)),
            ('VARIABLE', 'integer', ('INTEGER', 42)),
            ('VARIABLE', 'negative-int', ('INTEGER', -42)),
            ('VARIABLE', 'string', ('STRING', 'Hello World')),
            ('VARIABLE', 'bool-true', ('BOOLEAN', True)),
            ('VARIABLE', 'bool-false', ('BOOLEAN', False)),
            ('VARIABLE', 'name', ('IDENTIFIER', 'pi')),
        ]),

        # dot is decimal separator for floats
        ('variables/float_with_comma', SyntaxError),

        # leading zeros are not allowed
        ('variables/integer_leading_zeros', SyntaxError),
        ('variables/float_leading_zeros', SyntaxError),

        # String must be surrounded with double quotes
        ('variables/string_single_quote', SyntaxError),

        # Variables names can contain a-z, 0-9 and -
        ('variables/names', [
            ('VARIABLE', 'x', ('INTEGER', 1)),
            ('VARIABLE', 'xx', ('INTEGER', 2)),
            ('VARIABLE', 'abc', ('INTEGER', 3)),
            ('VARIABLE', 'abc1', ('INTEGER', 4)),
            ('VARIABLE', 'a-b-c', ('INTEGER', 5)),
            ('VARIABLE', '007', ('INTEGER', 6)),
            ('VARIABLE', '42x', ('INTEGER', 7)),
        ]),
        ('variables/name_uppercase', SyntaxError),
        ('variables/name_underscore', SyntaxError),

        # Variable name can't starts or ends with '-'
        ('variables/name_leading_minus', SyntaxError),
        ('variables/name_trailing_minus', SyntaxError),

        # Malformed definition
        ('variables/malformed_space_after_dolar', SyntaxError),
        ('variables/malformed_space_before_colon', SyntaxError),

        ### WIDGETS ###

        ### PARAGRAPHS ###

        #### Strong **xx** ####
        #### Italic //xx// ####
        #### Underline __xx__ ####
        #### Strikeout --xx-- ####
        #### Links ####
        #### References ####
        #### inline code ####
        #### automatic links ####
        #### variable interpolation ####
        #### char escaping ####
        #### sub / sup ^{} / _{} ####
        #### mark ==xx== ####
        #### smartarrows ####
        #### emoji ####

        
        #### LATEX $$xxx$$ ####

        ### ANCHORS ###

        ### FOOTNOTES ###

        ### BLOCKQUOTES ###

        ### LISTS ###


        ### OTHERS ###

        # Empty lines are ignored
        ('empty_lines', [('INLINE_COMMENT', 'guard')]),
    ])
    def test_tokenize(self, name, output):
        """
        Check result of tokenization on given test file.
        """
        with open(os.path.join(os.path.dirname(__file__), 'test_cases', name + '.mdoc')) as input:
            text = input.read()

            if isinstance(output, type):
                with self.assertRaises(output):
                    tokenize(text)
            else:
                self.assertEqual(tokenize(text), output)



if __name__ == '__main__':
    unittest.main()
