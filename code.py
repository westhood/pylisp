from const import *
from symbol import SymbolTable
from parser import Token
from xml.etree import ElementTree as ET

def inst2str(inst):
    operator, operand = inst
    if operator == OpBinOp:
        operand = BinOps[operand][0]
    elif operator == OpUnOp:
        operand = UnOps[operand][0]
    return "%s %s" % (VMOps[operator], operand)

UNDEF_VALUE = None

def GenExps(ast, symbol, generator):
    assert type(ast) == list
    for exp in ast:
        GenExp(exp, symbol, generator)
        generator.gen((OpPop, 1))

def GenExp(ast, symbol, generator, isTail=False):
    if not isinstance(ast, list):
        SinglarExp(ast, symbol, generator)
        return 
    type, info = ast[0].type, ast[0].info
    if type == "keyword":
        if info == "begin":
            GenSeq(ast, symbol, generator, isTail)
        elif info == "if":
            GenIf(ast, symbol, generator, isTail)
        elif info == "let":
            GenLet(ast, symbol, generator, isTail)
        elif info == "lambda":
            GenLambda(ast, symbol, generator, isTail)
        elif info == "lambda_v":
            GenLambdaV(ast, symbol, generator, isTail)
        elif info == "define":
            GenDefine(ast, symbol, generator, isTail)
        elif info == "call/cc":
            GenCallCC(ast, symbol, generator, isTail)
    elif type == "symbol":
        if info in Symbol2BinOp:
            GenBinOp(ast, symbol, generator, isTail)
        elif info in Symbol2UnOp:
            GenUnOp(ast, symbol, generator, isTail)
        else:
            GenCall(ast, symbol, generator, isTail)
    else:
        assert 0

def SinglarExp(ast, symbol, generator):
    assert not isinstance(ast, list)
    if ast.type == "symbol":
        symbol.genLoadSymbol(ast.info)
    elif ast.type in ("string", "number"):
        index = generator.consts.addLiteral(ast.info)
        generator.gen((OpLoadConst, index))
    else:
        assert 0

def GenSeq(ast, symbol, generator, isTail=False):
    """ (begin expr+ ) """
    assert ast[0].type == "keyword", ast[0].info == "begin"

    for exp in ast[1:-1]:
        GenExp(exp, symbol, generator)
        generator.gen((OpPop,1))

    # Value of a seq is last value of its expr. 
    last = ast[-1]
    GenExp(last, symbol, generator, True)

def GenIf(ast, symbol, generator, isTail=False):
    """ (if pred true false) """
    assert ast[0].type == "keyword" and ast[0].info == "if"
    assert len(ast) == 4

    pred = ast[1]
    true = ast[2]
    false = ast[3]

    GenExp(pred, symbol, generator)
    falsePatch = generator.gen((OpTest, None))
    GenExp(true, symbol, generator, isTail)
    endPatch = generator.gen((OpJump, None))
    generator.patchToHere(falsePatch)
    GenExp(false, symbol, generator, isTail)
    generator = generator.patchToHere(endPatch)

def GenUnOp(ast, symbol, generator, isTail=False):
    """ (UnOP expr) """
    assert ast[0].type == "symbol" and ast[0].info in Symbol2UnOp
    assert len(ast) == 2

    GenExp(ast[1], symbol, generator)
    generator.gen((OpUnOp, Symbol2UnOp[ast[0].info]))

def GenBinOp(ast, symbol, generator, isTail=False):
    """(BinOp x y)"""
    assert ast[0].type == "symbol" and ast[0].info in Symbol2BinOp
    assert len(ast) == 3

    GenExp(ast[1], symbol, generator)
    GenExp(ast[2], symbol, generator)
    generator.gen((OpBinOp, Symbol2BinOp[ast[0].info]))

def GenCall(ast, symbol, generator, isTail=False):
    """ (func arg*) """
    assert ast[0].type == 'symbol'

    sym = ast[0].info 
    symbol.genLoadSymbol(sym)

    argc = len(ast) - 1
    for arg in ast[1:]:
        GenExp(arg , symbol, generator)

    if isTail:
        generator.gen((OpTailCall, argc))
    else:
        generator.gen((OpCall, argc))

def GenDefine(ast, symbol, generator, isTail=False):
    """ (define name expr) """
    assert ast[0].type == "keyword" and ast[0].info == "define"
    assert not isinstance(ast[1], list) and ast[1].type == "symbol"
    assert len(ast) == 3

    scope, info = symbol.add(ast[1].info)
    GenExp(ast[2], symbol, generator)
    if scope == "global":
        generator.gen((OpSetGlobal, info))
    else:
        generator.gen((OpSetLocal, info))

    # Value of a define expr is None 
    generator.gen((OpLoadConst, 0))

def GenLet(ast, symbol, generator, isTail=False):
    """ (let (binds) expr """
    assert ast[0].type == "keyword" and ast[0].info == "let"
    assert len(ast) == 3

    binds, expr = ast[1:]
    proto = generator.proto
    # new scope for let 
    symbol.push()
    for item in binds:
        sym, expr0 = item[:] 
        assert sym.type == "symbol"
        GenExp(expr0, symbol, generator)
        scope, info = symbol.add(sym.info)
        assert scope == "local"
        generator.gen((OpSetLocal, info))
    GenExp(expr, symbol, generator, isTail)
    # close the scope
    proto.iLocalvars -= len(binds)
    scope_index = (symbol.current_scope()).index
    generator.gen((OpCloseUpvar, scope_index))
    symbol.pop()

def GenLambdaV(ast, symbol, generator, isTail=False, name=None):
    """ (lambda_v (arg1 arg2 . argv ) (body)) """
    assert ast[0].type == "keyword" and ast[0].info == "lambda_v"
    assert len(ast) == 3 

    # make a new proto.
    args = ast[1]
    # remove ". argv"
    proto = FunctionProto(len(args) - 2, True)
    proto.name = name
    generator.pushProto(proto)
    symbol.push(proto)
    # make new symbols for arguments.
    i = 0 
    for arg in args[:-2]:
        symbol.add(arg.info, {"local":i})
        i += 1
    assert args[-2].info == "."
    argv = args[-1].info
    symbol.add(argv, {"varg":True})
    GenExp(ast[2], symbol, generator, True)
    generator.gen((OpRet,1))
    symbol.pop()
    proto = generator.popProto()
    # load closure for lambda in original proto.
    generator.gen((OpBuildClosure, proto.indexInConsts))

def GenLambda(ast, symbol, generator, isTail=False, name=None):
    """ (lambda (arg1 arg2) (body)) """
    assert ast[0].type == "keyword" and ast[0].info in ("lambda", "lambda_v")

    # make a new proto.
    args = ast[1]
    body = ast[2:]
    proto = FunctionProto(len(args), False)
    proto.name = name
    generator.pushProto(proto)
    symbol.push(proto)
    # make new symbols for arguments.
    i = 0 
    for argname in ast[1]:
        info = {"local":i}
        symbol.add(argname.info, info)
        i += 1
    # gen code for body
    for expr in body[:-1]:
        GenExp(expr, symbol, generator, True)
        generator.gen((OpPop, 1))
    GenExp(body[-1], symbol, generator, True)
    generator.gen((OpRet,1))

    symbol.pop()
    proto = generator.popProto()
    # load closure for lambda in original proto.
    generator.gen((OpBuildClosure, proto.indexInConsts))

def GenCallCC(ast, symbol, generator, isTail=False, name=None):
    # FIXME:
    assert ast[0].type == "keyword" and ast[0].info == "call/cc"
    assert len(ast[1])
    GenExp(ast[1], symbol, generator, isTail)
    generator.gen((OpBuildContinuation, -1))
    generator.gen((OpCall, 1))

class CodeGenerator(object):
    def __init__(self, consts, proto):
        # pc indicates address of the next instruction to be generated. 
        self.pc = 0
        # main proto 
        self.proto = proto
        self.insts = proto.insts
        self.consts = consts
        self.stack = []
        pass

    def gen(self, code):
        self.insts.append(code)
        self.pc += 1
        # return address of the instruction just generated.
        return self.pc - 1

    def patchToHere(self, pc):
        assert self.insts[pc][0] in (OpTest, OpJump)
        assert self.pc >= pc
        self.insts[pc] = (self.insts[pc][0], self.pc - pc)

    def pushProto(self, proto):
        index = self.consts.addProto(proto)
        proto.indexInConsts = index
        self.stack.append((self.pc, self.proto))
        self.proto = proto
        self.insts = proto.insts
        self.pc = 0

    def popProto(self):
        oldProto = self.proto
        self.pc, self.proto = self.stack.pop()
        self.insts = self.proto.insts
        return oldProto

class ConstTable(object):
    def __init__(self):
        self.consts = [ UNDEF_VALUE ]
        self.literals = {}

    def addProto(self, value):
        self.consts.append(value)
        return len(self.consts) - 1

    def addLiteral(self, literal):
        if literal in self.literals:
            return self.literals[literal]
        self.consts.append(literal)
        index = len(self.consts) - 1 
        self.literals[literal] = index
        return index 

    def __getitem__(self, index):
        return self.consts[index]

    def __iter__(self):
        return self.consts.__iter__()

class FunctionProto(object):
    def __init__(self, argc, isvarg):
        self.argc = argc # number of arguments 
        self.isVararg = isvarg  
        self.insts = [] 
        # used to get size of localvars in frame object.
        self.maxLocalvars = argc 
        # index of next free localvar 
        self.iLocalvars = argc
        self.upvars = []

    def adjustMaxLocalvars(self):
        if self.iLocalvars > self.maxLocalvars:
            self.maxLocalvars = self.iLocalvars

    def __str__(self):
        head = ET.Element("head", {"argc":str(self.argc), 
            "varg":str(self.isVararg), "maxLocalvars":str(self.maxLocalvars)
            })

        upvars = ET.Element("upvars")
        for upvar in self.upvars:
            sub = ET.Element("upvar")
            sub.text = "%s %s" % upvar
            upvars.append(sub)

        insts = ET.Element("insts")
        for inst in self.insts:
            sub = ET.Element("inst")
            sub.text = inst2str(inst)
            insts.append(sub)

        proto = ET.Element("proto")
        proto.append(head)
        proto.append(upvars)
        proto.append(insts)

        return ET.tostring(proto)

def generate(ast):
    """ generate(ast) => constTable """
    consts = ConstTable()
    main = FunctionProto(0, False)
    generator = CodeGenerator(consts, main)
    symbols = SymbolTable(generator)
    GenExps(ast, symbols, generator)
    consts.addProto(main)
    return consts
