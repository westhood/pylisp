import runtime 
import operator 

__all__ = [
"OpRet", 
"OpLoad", 
"OpLoadLocal", 
"OpBinOp", 
"OpCall", 
"OpJump", 
"OpTest", 
"OpLoadConst", 
"OpTailCall", 
"OpPop", 
"OpUnOp", 
"OpLoadVarg",
"OpSetLocal", 
"OpLoadLocal", 
"OpLoadGlobal", 
"OpSetGlobal",
"OpBuildClosure", 
"OpLoadUpvar", 
"OpCloseUpvar",
"OpSetUpvar",
"OpBuildClosure",
"OpBuildContinuation",
"OpHalt",
"VMOps",
"BinOps",
"UnOps",
"Symbol2UnOp",
"Symbol2BinOp"
]

OpRet = 1
OpLoad = 2
OpLoadLocal = 3 
OpBinOp = 4
OpCall = 5
OpJump = 6
OpTest = 7
OpLoadConst = 8
OpTailCall = 9
OpPop = 10
OpUnOp = 11
OpSetLocal = 12
OpLoadLocal = 13
OpLoadGlobal = 14
OpBuildClosure = 15
OpLoadUpvar = 16
OpCloseUpvar = 17
OpSetGlobal = 18
OpLoadVarg = 19
OpSetUpvar = 20
OpBuildContinuation = 21
OpHalt = 22


VMOps = dict([ (v,k) for k,v in globals().copy().items() if k.startswith("Op") ])

BinOps = dict([
        (1, ("+", operator.add)),
        (2, ("-", operator.sub)),
        (3, ("*", operator.mul)),
        (4, ("/", operator.div)),
        (5, ("cons", runtime.cons)),
        (6, ("=", operator.eq)),
        (7, (">", operator.gt)),
        ])

Symbol2BinOp = dict([ (v[0], k) for k,v in BinOps.items() ])

UnOps = dict([
        (1, ("-", operator.neg)),
        (2, ("car", runtime.car)),
        (3, ("cdr", runtime.cdr)),
        ])

Symbol2UnOp = dict([ (v[0], k) for k,v in UnOps.items() ])


