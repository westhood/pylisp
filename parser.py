import re
from itertools import ifilter


class ParseException(Exception):
    pass


class Token(object):
    __slots__ = ['info', 'type', 'lineno', 'position']

    def __init__(self, type, info):
        self.type = type
        self.info = info

    def __str__(self):
        if self is not EOF_TOKEN:
            return "Token(%s, %s)" % (self.type, self.info)
        else:
            return "Token(EOF)"

    __repr__ = __str__

    def __eq__(self, other):
        if self.type == other.type and self.info == other.info:
            return True
        else:
            return False

EOF_TOKEN = Token(None, None)


def str2num(s):
    if s.find(".") != -1:
        return float(s)
    else:
        return int(s)


PATTERNS = [
    ('whitespace', r'([ \t\r\f\v])'),
    ('newline', r'(\n)'),
    ('comment', r'(;[^\n]*)'),
    ('lparen', r'(\()'),
    ('rparen', r'(\))'),
    ('number', r'''([+\-]? ## optional sign,
                   (?:     ## followed by some decimals
                       \d+\.\d+
                     | \d+\.
                     | \.\d+
                     | \d+))
                '''),
    ('symbol', r'''([a-zA-Z\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]
                   [\w\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]*)'''),
    ('string', r'("([^\"] | \\")*")'),
    ('quote', r'(\')'),
    ('backquote', r'(`)'),
    ('comma', r'(,)'),
]


class Lexer(object):
    skip = ("comment", "whitespace", "newline")
    token_ptn = re.compile("|".join(["(?P<%s>%s)" % (n, e) for n, e in PATTERNS]),
                           re.VERBOSE)
    keywords = {"define", "let", "lambda", "lambda_v", "if", "begin"}

    def __init__(self, src):
        self.s = src
        self.buffer = []
        self.tokens = ifilter(lambda x: x.type not in self.skip, self.tokenize(src))

    def tokenize(self, s):
        lineno = 1
        position = 0
        offset = 0
        token_ptn = self.token_ptn

        while 1:
            m = token_ptn.match(s, offset)
            if not m:
                break

            groups = filter(lambda x: x[1] is not None, m.groupdict().items())
            assert len(groups) == 1
            name, value = groups[0]

            if name == "newline":
                position = 0

            token = Token(name, value)
            token.lineno = lineno
            token.position = position

            if name == "newline":
                position = 0
            elif name == "number":
                token.info = str2num(value)
            elif name == "symbol" and value in self.keywords:
                token.type = "keyword"

            yield token

            span = m.span()[1] - m.span()[0]
            position += span
            offset = m.end()

        yield EOF_TOKEN

    def next(self):
        if self.buffer:
            return self.buffer.pop()
        else:
            try:
                next = self.tokens.next()
                return next
            except StopIteration:
                return

    def push(self, v):
        self.buffer.append(v)


class Parser(object):
    def __init__(self, src):
        self.lexer = Lexer(src)

    def exprs(self):
        lexer = self.lexer
        ast = []
        while 1:
            token = lexer.next()
            if token is EOF_TOKEN or not token:
                return ast
            else:
                lexer.push(token)
                ast.append(self.expr())

    def expr(self):
        """ expr => ( expr* ) | s | `expr """
        lexer = self.lexer
        token = lexer.next()

        if token is EOF_TOKEN or not token:
            raise ParseException()

        if token.type == "lparen":
            ast = []
            while 1:
                next = lexer.next()
                if next.type != "rparen":
                    lexer.push(next)
                    ast.append(self.expr())
                else:
                    return ast
        elif token.type == "backquote":
            ast = [Token("keyword", "quote")]
            ast.append(self.expr())
            return ast
        else:
            return token


def traverse(ast, visitor):
    children = visitor(ast, "pre")
    for child in children:
        sub = reduce(lambda x, y: x[y], child, ast)
        traverse(sub, visitor)
    visitor(ast, "post")


def check_token(token, type, info):
    try:
        return token.type == type and token.info == info
    except AttributeError:
        return False


class Transform(object):
    def pre(self, ast):
        # FIXME:
        if not ast:
            return []
        if type(ast) == Token:
            return []
        elif (check_token(ast[0], "keyword", "define") and
                type(ast[1]) == list and
                len(ast[1]) >= 1):
            body = ast[2:]
            name, args = ast[1][0], ast[1][1:]
            ast[1] = name
            ast[2] = [Token("keyword", "lambda"), args] + body
            # keeps only ast[:3]
            del ast[3:]
            return [(2,)]
        # XXX: more transform to be added here.
        elif (check_token(ast[0], "keyword", "lambda") and
                len(ast[1]) >= 2 and
                check_token(ast[1][-2], "symbol", ".")):
            ast[0] = Token("keyword", "lambda_v")
            return [(2,)]
        else:
            return [(x,) for x in range(0, len(ast))]

    def post(self, ast):
        pass

    def __call__(self, ast, phase):
        if phase == "pre":
            return self.pre(ast)
        elif phase == "post":
            return self.post(ast)
        else:
            assert 0
