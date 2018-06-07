import re, sys


MULTI_LINE_COMMENT = re.compile('\A"""(.*?)"""\s*?$\\n?', re.MULTILINE | re.DOTALL)
SINGLE_LINE_COMMENT = re.compile('\A([^;\n]*);(.*)$', re.MULTILINE)

EMPTY_LINE = re.compile('\A\s*$\\n?', re.MULTILINE)

IDENTIFIER = '\$([-a-z0-9]+)'
IDENTIFIER_REGEXP = re.compile(f'\A{IDENTIFIER}\Z')
VARIABLE = re.compile(f'\A{IDENTIFIER}:\s*(.+?)\s*$\\n?', re.MULTILINE)

STRING = '"(.*)"'
STRING_REGEXP = re.compile(f'\A{STRING}\Z')

FLOAT = '-?[0-9]+\.[0-9]+'
FLOAT_REGEXP = re.compile(f'\A{FLOAT}\Z')

INTEGER = '-?[0-9]+'
INTEGER_REGEXP = re.compile(f'\A{INTEGER}\Z')

BOOLEAN = '(true|false)'
BOOLEAN_REGEXP = re.compile(f'\A{BOOLEAN}\Z')

HEADING = re.compile('\A(#{1,3}) (.*) \\1\\s*$\\n\\n', re.MULTILINE)

PARAMETER = f'\s*([-a-z0-9]+)\s*=\s*({STRING}|{FLOAT}|{INTEGER}|{BOOLEAN}|{IDENTIFIER})\s*'
PARAMETER_REGEXP = re.compile(PARAMETER)

WIDGET_INLINE_REGEXP = re.compile(f'\A@([-a-z0-9]+)\((\s*|{PARAMETER}(,{PARAMETER})*)\)\s*$', re.MULTILINE)

def read_multiline_comment(text, offset):
    if not text.startswith('"""'):
        return None

    m = MULTI_LINE_COMMENT.match(text)
    if m is None:
        raise SyntaxError("Broken multi line comment at %d" % (offset, ))
    match_length = len(m.group())

    return (text[match_length:], offset + match_length, ('MULTILINE_COMMENT', m.group(1)))


def read_singleline_comment(text, offset):
    m = SINGLE_LINE_COMMENT.match(text)
    if m is None:
        return None

    match_length = len(m.group())
    return (m.group(1) + ' '*(len(m.group(2))+1) + text[match_length:], offset, ('SINGLE_LINE_COMMENT', m.group(2)))


def read_empty_line(text, offset):
    m = EMPTY_LINE.match(text)
    if m is None:
        return None

    match_length = len(m.group())
    return (text[match_length:], offset + match_length, ('EMPTY_LINE', ))


def read_heading(text, offset):
    if not text.startswith('#'):
        return None
    m = HEADING.match(text)
    if m is None:
        raise SyntaxError('Broken heading at %d: \'%s\'' % (offset, text[:20]))
    match_length = len(m.group())
    return (text[match_length:], offset + match_length, ('HEADING', len(m.group(1)), m.group(2)))

def read_widget(text, offset):
    """

    ('WIDGET', <name>, <params>, <block>)
    """
    if not text.startswith('@'):
        return None
    m = WIDGET_INLINE_REGEXP.match(text)
    if m is None:
        raise SyntaxError('Broken widget open tag at %d: \'%s\'' % (offset, text[:20]))
    else:
        match_length = len(m.group())
        print(">>>", m.group(2), "<<<")
        params = PARAMETER_REGEXP.findall(m.group(2))
        print('--- ', params)

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

    SyntaxError('Broken variable value at %d: %s' % (-1, value))


def read_variable(text, offset):
    if not text.startswith('$'):
        return None

    m = VARIABLE.match(text)
    if m is None:
        raise SyntaxError('Broken variable definition at %d: \'%s\'' % (offset, text[:20]))
    name, value = m.group(1), m.group(2)
    match_length = len(m.group())

    return (text[match_length:], offset + match_length, ('VARIABLE', name, *read_value(value)))


def parse(text):
    readers = [
        read_multiline_comment,
        read_singleline_comment,
        read_variable,
        read_heading,
        read_widget,
        read_empty_line
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
        print(token)
    return tokens


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        parse(f.read())
