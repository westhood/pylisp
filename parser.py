import re 
import sys

class ParseException(Exception):pass

KEYWORDS = set(["define", "let", "lambda","lambda_v","if", "begin","call/cc"]) 

"""Here are the patterns we pay attention when breaking down a string
into tokens."""
PATTERNS = [ ('whitespace', re.compile(r'(\s+)')),
             ('newline', re.compile(r'(\n)')),
             ('comment', re.compile(r'(;[^\n]*)')),
             ('(', re.compile(r'(\()')),
             (')', re.compile(r'(\))')),
             ('number', re.compile(r'''( [+\-]?    ## optional sign,
                                         (?:       ## followed by some
                                                   ## decimals
                                            \d+\.\d+
                                            | \d+\.
                                            | \.\d+
                                            | \d+
                                         )
                                       )
                                    ''',
                                   re.VERBOSE)),
             ('symbol',
              re.compile(r'''([a-zA-Z\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]
                              [\w\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]*)''',
                                   re.VERBOSE)),
             ('string', re.compile(r'''
                                      "
                                      (([^\"] | \\")*)
                                      "
                                      ''',
                                   re.VERBOSE)),
             ('\'', re.compile(r'(\')')),
             ('`', re.compile(r'(`)')),
             ## fixme: add UNQUOTE-SPLICING form as well
             (',', re.compile(r'(,)')),
             ]

class Token(object):
    def __init__(self, type, info):
        self.type = type
        self.info = info

    def __str__(self):
        return "Token(%s, '%s')" % (self.type, self.info)

    __repr__ = __str__

    def __eq__(self, other):
        if type(self) == type(other) \
           and self.type == other.type \
           and self.info == other.info:
            return True
        else:
            return False

EOF_TOKEN = Token(None, None)

def str2num(s):
    if s.find(".") != -1:
        return float(s)
    else:
        return int(s)

def tokenize(s):
    """Given a string 's', generate a list of its tokens. """
    lineno = 1
    position = 0

    while 1:
        should_continue = 0

        for tokenType, regex in PATTERNS:
            match_obj = regex.match(s)
            if match_obj:
                if tokenType == "newline":
                    lineno +=1
                    position = 0
                    continue 

                info = match_obj.group(1)
                if tokenType == "symbol" and info in KEYWORDS:
                    token = Token("keyword", info) 
                elif tokenType == "number":
                    token = Token(tokenType, str2num(info))
                else:
                    token = Token(tokenType, info)
                token.lineno = lineno
                token.position = position
                yield token

                should_continue = 1
                s = s[match_obj.span()[1]:]
                position += match_obj.span()[1]

        if should_continue == 0:
            break

class Lexer(object):
    def __init__(self,tokens):
        self.tokens = tokens
        self.buffer = []

    def next(self):
        if self.buffer:
            return self.buffer.pop()
        else:
            try:
                next = self.tokens.next()
                return next
            except StopIteration:
                return next

    def push(self, token):
        self.buffer.append(token)

def expr(tokens):
    """ expr => ( expr* ) | s | `expr """
    token = tokens.next()
    if token is EOF_TOKEN or not token:
        raise ParseException()

    if token.type == "(":
        ast = []
        while 1:
            next = tokens.next()
            if next.type != ")":
                tokens.push(next)
                ast.append(expr(tokens))
            else:
                return ast 
    elif token.type == "`":
        ast = [Token("keyword", "quote")]
        ast.append(expr(tokens))
        return ast
    else:
        return token

def exprs(tokens):
    ast = []
    while 1:
        token = tokens.next()
        if token is EOF_TOKEN or not token:
            return ast
        else:
            tokens.push(token)
            ast.append(expr(tokens))

def traverse(ast , visitor):
    children = visitor(ast, "pre")
    for child in children:
        sub = reduce(lambda x,y: x[y], child, ast)
        traverse(sub, visitor)
    visitor(ast,"post")
    
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
        elif check_token(ast[0], "keyword", "define") and \
             type(ast[1]) == list and \
             len(ast[1]) >= 1:
            body = ast[2:] 
            name, args = ast[1][0], ast[1][1:]
            ast[1] = name
            ast[2] = [ Token("keyword", "lambda"), args ] + body
            # keeps only ast[:3]
            del ast[3:]
            return [(2,)]
        # XXX: more transform to be added here.
        elif check_token(ast[0], "keyword", "lambda") and \
             len(ast[1]) >= 2 and \
             check_token(ast[1][-2], "symbol", "."):
            ast[0] = Token("keyword", "lambda_v")
            return [(2,)]
        else:
            return [ (x,) for x in range(0,len(ast))]

    def post(self, ast):pass

    def __call__(self, ast, phase):
        if phase == "pre":
            return self.pre(ast)
        elif phase == "post":
            return self.post(ast)
        else: assert 0
 
from itertools import ifilter

class TokenFilter(object):
    def __init__(self, pred):
        self.pred = pred 

    def __call__(self, generator):
        return ifilter(self.pred, generator())

class Lexer(object):
    def __init__(self,  s):
        self.s = s
        self.buffer = []
        skip = ("comment", "whitespace", "newline")
        self.tokens = ifilter(lambda x: x.type not in skip, self.gen_tokens()) 

    def gen_tokens(self):
        lineno = 0
        for line in self.s:
            lineno += 1
            for token in tokenize(line):
                token.lineno = lineno
                if token.type == "newline":
                    lineno += 1
                yield token
            yield Token("newline", "\n")
        yield EOF_TOKEN
        
    def next(self):
        if self.buffer:
            return self.buffer.pop()
        else:
            try:
                next = self.tokens.next()
                return next
            except StopIteration:
                return next

    def push(self, v):
        self.buffer.append(v)
        return self

if __name__ == '__main__':pass
