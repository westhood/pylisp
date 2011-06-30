import unittest
import parser
import code
import vm
import pdb
import cStringIO
import runtime


def compile(source):
    s = cStringIO.StringIO(source)
    lex = parser.Lexer(s)
    visitor = parser.Transform()
    ast = parser.exprs(lex)
    parser.traverse(ast, visitor)
    consts = code.generate(ast)
    return consts

s = """
(define (func x)
    (call/cc 
        (lambda (f)
            (if x (f 2) 3))))
(display (func 1))
(display (func 0))
"""
consts = compile(s)

def display(*args):
    for arg in args:
        print arg,
    print ""
    return [None]

vm.VM(consts, {"display": display}).start()
