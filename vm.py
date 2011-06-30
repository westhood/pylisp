from const import *
from runtime import *
import runtime 

def inst2str(inst):
    operator, operand = inst
    if operator == OpBinOp:
        operand = BinOps[operand][0]
    elif operator == OpUnOp:
        operand = UnOps[operand][0]
    return "%s  %s" % (VMOps[operator], operand)

class DummyFrame(object):pass
class VMException(Exception):pass

def clone(frame):
    new = DummyFrame()
    new.proto = frame.proto
    new.insts = frame.insts
    new.upvars = frame.upvars
    new.localvars = frame.localvars[:]
    new.stack = frame.stack[:]
    new.to_be_forked = False
    
    if hasattr(frame,"varargs"):
        new.varargs = frame.varargs
    
    if hasattr(frame,"saved_pc"):
        new.saved_pc = frame.saved_pc
    return new 

class Frame(object):
    def __init__(self, proto, upvars, args):
        self.proto = proto
        self.insts = proto.insts
        self.args = args
        self.upvars = upvars
        self.to_be_forked = False

        self.localvars = [None] * proto.maxLocalvars

        if proto.isVararg:
            if len(args) >= proto.argc:
                self.localvars[:proto.argc] = args[:proto.argc]
                self.varargs = runtime.build_list(args[proto.argc:])
            else:
                raise VMException("args:%s argc:%s varg:%s"
                        % (len(args), proto.argc, proto.isVararg))
        else:
            if len(args) == proto.argc:
                self.localvars[:proto.argc] = args[:]
            else:
                raise VMException("args:%s argc:%s varg:%s"
                        % (len(args), proto.argc, proto.isVararg))

        self.stack = []

def fork_frames(frames):
    # FIXME
    if frames.cdr() == None:
        old = frames.car()
        new = clone(old)
        return LinkList(new), LinkList(old)

    upper = frames.cdr().car()
    upper.to_be_forked = True
    current = frames.car()
    new = clone(current)
    news = frames.cdr().cons(new)
    return news, frames

class Continuation(object):pass


def close_upvars(frame, scope_index):
    for upvar in frame.upvars:
        if upvar.frame is frame and upvar.scope_index == index:
            upvar.close()

class VM(object):
    def __init__(self, consts, env, entry=None):
        self.consts = consts
        self.env = env
        if entry == None:
            entry = consts[-1]
        frame = Frame(entry, [], [])
        frames = LinkList(frame)
        self.frames = frames

    def start(self):
        env = self.env
        consts = self.consts
        frames = self.frames
        frame = frames.car()
        insts = frame.insts
        pc = 0

        while True:
            try:
                operator, operand = insts[pc]
                # print inst2str(insts[pc])
                #print frame.stack
            except IndexError:
                # print "return"
                return 

            if operator == OpLoadLocal:  
                assert operand >= 0
                var = frame.localvars[operand]
                assert var is not None
                frame.stack.append(var)

            elif operator == OpSetLocal:
                assert operand >= 0
                a = frame.stack.pop()
                frame.localvars[operand] = a

            elif operator == OpLoadGlobal:
                a = consts[operand]
                frame.stack.append(env[a])

            elif operator == OpSetGlobal:
                b = frame.stack.pop()
                s = consts[operand]
                env[s] = b

            elif operator == OpLoadUpvar:
                assert operand >= 0 
                var = frame.upvars[operand].get()
                frame.stack.append(var)

            elif operator == OpSetUpvar:
                a = frame.stack.pop()
                assert operand >= 0 
                frame.upvars[operand].set(a)

            elif operator == OpLoadVarg:
                frame.stack.append(frame.varargs)

            elif operator ==  OpLoadConst:
                try:
                    var = consts[operand]
                    frame.stack.append(var)
                except IndexError:
                    raise VMException("Error const index '%s' " % operand)

            elif operator == OpBinOp:
                b = frame.stack.pop()
                a = frame.stack.pop()
                try: 
                    frame.stack.append(BinOps[operand][1](a,b))
                except KeyError:
                    raise VMException("Unknown BinOp '%s' " % operand)

            elif operator == OpUnOp:
                a = frame.stack.pop()
                try:
                    symbol, unop = UnOps[operand]
                    frame.stack.append(unop(a))
                except KeyError:
                    raise VMException("Unknown UnOp '%s' " % operand)
 
            elif operator == OpCall:
                # build new frame
                if operand > 0:
                    args = frame.stack[-operand:]
                    frame.stack = frame.stack[:-operand]
                else:
                    args = []
                closure = frame.stack.pop()

                if isinstance(closure, Closure):
                    proto = closure.proto
                    upvars = closure.upvars
                    new_frame = Frame(proto, upvars, args)
                    # save current pc
                    frame.saved_pc = pc
                    frames = frames.cons(new_frame)
                    frame = frames.car()
                    insts = frame.insts
                    pc = 0
                    continue

                elif isinstance(closure, Continuation):
                    frames = closure.frames
                    frame = frames.car()
                    insts = frame.insts
                    pc = frame.saved_pc
                    assert len(args) == 1
                    frame.stack.extend(args)

                else:
                    ret = closure(*args)
                    frame.stack.extend(ret)

            elif operator == OpTailCall:
                args = []
                for i in xrange(0, operand):
                    args.append(frame.stack.pop())
                args.reverse()
                closure = frame.stack.pop()

                if isinstance(closure, Closure):
                    proto = closure.proto
                    upvars = closure.upvars
                    new_frame = Frame(proto, upvars, args)
                    frames = frames.cdr().cons(new_frame)
                    frame = frames.car()
                    insts = frame.insts
                    pc = 0
                    continue

                elif isinstance(closure, Continuation):
                    frames = closure.frames
                    frame = frames.car()
                    insts = frame.insts
                    pc = frame.saved_pc
                    assert len(args) == 1
                    frame.stack.extend(args)

                else:
                    ret = closure(*args)
                    frame.stack.extend(ret)

            elif operator == OpRet:
                rets = frame.stack[-operand:]
                close_upvars(frame, 0)
                # load upper frame
                frames = frames.cdr()
                if frames.car().to_be_forked:
                    new, old = fork_frames(frames)
                    frames = new 
                frame = frames.car()
                pc = frame.saved_pc
                insts = frame.insts
                frame.stack.extend(rets)
            
            elif operator == OpBuildContinuation:
                new, old = fork_frames(frames)
                old.car().stack.pop()
                old.car().saved_pc = pc + 1
                cc = Continuation()
                cc.frames = old
                frames = new
                frame = frames.car()
                frame.stack.append(cc)

            elif operator == OpJump:
                pc += operand
                continue

            elif operator == OpTest:
                """
                (if (= x 2) (a) (b)) 
                # In the end , only the value of whole "if" 
                # expression is on the top of the stack.
                Load      x
                LoadConst 2
                EQ
                TEST 3
                LOAD A
                JUMP 2
                LOAD B
                """
                isTrue = frame.stack.pop()
                if not isTrue:
                    pc += operand
                    continue

            elif operator == OpPop:
                for i in xrange(0, operand):
                    frame.stack.pop()

            elif operator == OpCloseUpvar:
                scope_index = operand
                close_upvars(frame, scope_index)

            elif operator == OpBuildClosure:
                a = frame.stack.pop()
                closure = Closure(a, frame)
                frame.stack.append(closure)

            elif operator == OpHalt:
                return 
            else:
                raise VMException("Unknown VM operator with operand %s:%s ." 
                        % (operator,operand))
            pc += 1
