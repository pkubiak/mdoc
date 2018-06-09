import unittest, sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from parameterized import parameterized
from mdoc.parser import tokenize


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

        # Widget require to proceded by double new line
        ('widgets/no_new_line', SyntaxError),

        # When there is no params or body, brackets can be ommited but it is not required
        ('widgets/no_params_no_body_01', [('WIDGET', 'widget', {}, None), ('INLINE_COMMENT', 'guard')]),
        ('widgets/no_params_no_body_02', [('WIDGET', 'widget', {}, None), ('INLINE_COMMENT', 'guard')]),
        ('widgets/no_params_no_body_03', [('WIDGET', 'widget', {}, None), ('INLINE_COMMENT', 'guard')]),
        ('widgets/no_params_empty_body_01', [('WIDGET', 'widget', {}, ''), ('INLINE_COMMENT', 'guard')]),
        ('widgets/no_params_empty_body_02', SyntaxError),
        ('widgets/no_params_empty_body_01', [('WIDGET', 'widget', {}, ''), ('INLINE_COMMENT', 'guard')]),

        # Widget with params
        ('widgets/inline_params', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True), 'pi': ('FLOAT', 3.14), 'parent': ('IDENTIFIER', 'root')}, None)]),
        ('widgets/multiline_params', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg'), 'margin': ('INTEGER', 5), 'border': ('BOOLEAN', True), 'pi': ('FLOAT', 3.14), 'parent': ('IDENTIFIER', 'root')}, None)]),

        # Whitespaces doesn't metter
        ('widgets/params_whitespaces', [('WIDGET', 'image', {'src': ('STRING', 'img.jpg')}, None)]),

        # Widget can't contain duplicated parameters
        ('widgets/params_duplicated', SyntaxError),


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
