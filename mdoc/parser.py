import re, sys
# from renderers.html import HTMLRenderer


MULTI_LINE_COMMENT = re.compile('\A"""(.*?)"""\s*?$\\n?', re.MULTILINE | re.DOTALL)
SINGLE_LINE_COMMENT = re.compile('\A([^;\n]*);(.*)$', re.MULTILINE)

EMPTY_LINE = re.compile('\A\s*$\\n?', re.MULTILINE)

IDENTIFIER = '\$([a-z0-9][a-z0-9]?|[a-z0-9][-a-z0-9]+[a-z0-9])'
IDENTIFIER_REGEXP = re.compile(f'\A{IDENTIFIER}\Z')
VARIABLE = re.compile(f'\A{IDENTIFIER}:\s*(.+?)\s*$\\n?', re.MULTILINE)

STRING = '\\"(.*)\\"'
STRING_REGEXP = re.compile(f'\A{STRING}\Z')

FLOAT = '-?([0-9]|[1-9][0-9]+)\.[0-9]+'
FLOAT_REGEXP = re.compile(f'\A{FLOAT}\Z')

INTEGER = '-?([0-9]|[1-9][0-9]+)'
INTEGER_REGEXP = re.compile(f'\A{INTEGER}\Z')

BOOLEAN = '(true|false)'
BOOLEAN_REGEXP = re.compile(f'\A{BOOLEAN}\Z')

HEADING = re.compile('\A(#{1,3}) (.*) \\1\\s*$\\n\\n', re.MULTILINE)

PARAMETER = f'\s*([-a-z0-9]+)\s*=\s*({STRING}|{FLOAT}|{INTEGER}|{BOOLEAN}|{IDENTIFIER})\s*'
PARAMETER_REGEXP = re.compile(PARAMETER)

WIDGET_INLINE = f'%([-a-z0-9]+)\((\s*|{PARAMETER}(,{PARAMETER})*)\)\s*'
WIDGET_INLINE_REGEXP = re.compile(f'\A{WIDGET_INLINE}$', re.MULTILINE)
WIDGET_LINE = f'^(  |\\t).*$\\n'
WIDGET_WITH_BLOCK = f'\A{WIDGET_INLINE}({{\\n({WIDGET_LINE})*}})?$'
WIDGET_WITH_BLOCK_REGEXP = re.compile(WIDGET_WITH_BLOCK, re.MULTILINE)

LINE = '^(?!\s+$).*$\\n'
PARAGRAPH = f'({LINE})+?^\s*$\\n'
PARAGRAPH_REGEXP = re.compile(f'\A{PARAGRAPH}', re.MULTILINE)


def read_block_comment(text, offset):
    if not text.startswith('"""'):
        return None

    m = MULTI_LINE_COMMENT.match(text)
    if m is None:
        raise SyntaxError("Broken block comment at %d" % (offset, ))
    match_length = len(m.group())

    return (text[match_length:], offset + match_length, ('BLOCK_COMMENT', m.group(1).strip()))


def read_inline_comment(text, offset):
    m = SINGLE_LINE_COMMENT.match(text)
    if m is None:
        return None

    match_length = len(m.group())
    return (m.group(1) + ' '*(len(m.group(2))+1) + text[match_length:], offset, ('INLINE_COMMENT', m.group(2).strip()))


def read_empty_line(text, offset):
    """
    Empty line doesn't produce any tokens
    """
    m = EMPTY_LINE.match(text)
    if m is None:
        return None

    match_length = len(m.group())
    return (text[match_length:], offset + match_length, None)


def read_heading(text, offset):
    if not text.startswith('#'):
        return None
    m = HEADING.match(text)
    if m is None:
        raise SyntaxError('Broken heading at %d: \'%s\'' % (offset, text[:20]))
    match_length = len(m.group())
    return (text[match_length:], offset + match_length, ('HEADING', len(m.group(1)), m.group(2).strip()))

def read_widget(text, offset):
    """

    ('WIDGET', <name>, <params>, <block>)
    """
    if not text.startswith('%'):
        return None
    m = WIDGET_WITH_BLOCK_REGEXP.match(text)
    if m is None:
        raise SyntaxError('Broken widget open tag at %d: \'%s\'' % (offset, text[:20]))
    else:
        match_length = len(m.group())
        # print(">>>", m.group(2), "<<<")
        params = PARAMETER_REGEXP.findall(m.group(2))
        # print('--- ', params)
        params = {name: read_value(value) for name, value, *_ in params}
        return (text[match_length:], offset + match_length, ('WIDGET', m.group(1), params, None))


def read_value(value):
    m = STRING_REGEXP.match(value)
    if m: return ('STRING', m.group(1))

    m = FLOAT_REGEXP.match(value)
    if m: return ('FLOAT', float(m.group()))

    m = INTEGER_REGEXP.match(value)
    if m: return ('INTEGER', int(m.group()))

    m = BOOLEAN_REGEXP.match(value)
    if m: return ('BOOLEAN', m.group() == 'true')

    m = IDENTIFIER_REGEXP.match(value)
    if m: return ('IDENTIFIER', m.group(1))

    raise SyntaxError('Broken variable value at %d: %s' % (-1, value))


def read_variable(text, offset):
    if not text.startswith('$'):
        return None

    m = VARIABLE.match(text)
    if m is None:
        raise SyntaxError('Broken variable definition at %d: \'%s\'' % (offset, text[:20]))
    name, value = m.group(1), m.group(2)
    match_length = len(m.group())

    return (text[match_length:], offset + match_length, ('VARIABLE', name, read_value(value)))


def read_paragraph(text, offset):
    m = PARAGRAPH_REGEXP.match(text)
    if not m:
        return None
    match_length = len(m.group())
    return (text[match_length:], offset + match_length, ('PARAGRAPH', m.group()))


def tokenize(text):
    """
    Parse `text` into list of tokens.
    """
    readers = [
        read_block_comment,
        read_inline_comment,
        read_empty_line,
        read_variable,
        read_heading,
        read_widget,
        read_paragraph
    ]
    offset = 0
    tokens = []

    while len(text) > 0:
        for reader in readers:
            response = reader(text, offset)
            if response is not None:
                text, offset, token = response
                if token is not None:
                    tokens.append(token)
                break
        else:
            raise SyntaxError("Unknown syntax at %d: '%s'" % (offset, text[:20]))
        # print(token)
    return tokens


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        tokens = tokenize(f.read())
        print(tokens)
        HTMLRenderer.render()
