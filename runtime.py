import cStringIO


class Closure(object):
    def __init__(self, proto, frame):
        self.proto = proto
        self.upvars = []

        for kind, index, scope_index in proto.upvars:
            if kind == "local":
                upvar = Upvar(frame, index, scope_index)
                self.upvars.append(upvar)
            elif kind == "varg":
                self.upvars.append(UpvarForVarg(frame))
            elif kind == "up":
                self.upvars.append(frame.upvars[index])
            else:
                assert 0


class UpvarForVarg(object):
    def __init__(self, frame):
        self.frame = frame
        self.closed = False
        self.scope_index = 0

    def get(self):
        if self.closed:
            return self.value
        else:
            return self.frame.varargs

    def set(self, value):
        if self.closed:
            self.value = value
        else:
            self.frame.varargs = value

    def close(self):
        if not self.closed:
            self.value = self.frame.varargs
            del self.frame
            self.closed = True


class Upvar(object):
    CLOSED = 0
    OPEN = 1

    def __init__(self, frame, index, scope_index):
        self.frame = frame
        self.index = index
        self.stat = Upvar.OPEN
        self.scope_index = scope_index

    def get(self):
        if self.stat == Upvar.CLOSED:
            return self.value
        else:
            return self.frame.localvars[self.index]

    def set(self, value):
        if self.stat == Upvar.CLOSED:
            self.value = value
        else:
            self.frame.localvars[self.index] = value

    def close(self):
        print "close"
        assert self.stat == Upvar.OPEN
        self.value = self.frame.localvars[self.index]
        del self.frame
        self.stat == Upvar.CLOSED


def build_list(seq):
    ret = None
    for i in reversed(seq):
        if isinstance(i, list):
            i = build_list(i)
        ret = cons(i, ret)
    return ret


def sclist2pylist(l):
    ret = []
    while l:
        head, l = l.car(), l.cdr()
        if isinstance(head, LinkList):
            head = sclist2pylist(head)
        ret.append(head)
    return ret


class LinkList(object):
    def __init__(self, v, next=None):
        self.v = v
        self.next = next

    def cons(self, v):
        new = LinkList(v)
        new.next = self
        return new

    def car(self):
        return self.v

    def cdr(self):
        return self.next

    def __str__(self):
        n = self
        sb = cStringIO.StringIO()
        sb.write("(%s" % self.v)
        try:
            while n.next:
                n = n.next
                sb.write(" %s" % str(n.v))
        except AttributeError:
            sb.write(" . %s" % n)
        sb.write(")")
        return sb.getvalue()

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        if self is other:
            return True

        return list_eq(self, other)


def list_eq(a, b):
    while 1:
        if a.car() != b.car():
            return False

        a, b = a.cdr(), b.cdr()
        if a is None and b is None:
            return True
        elif a is None or b is None:
            return False


def cons(x, y):
    if not isinstance(y, LinkList):
        return LinkList(x, next=y)
    else:
        return y.cons(x)


def car(x):
    if not isinstance(x, LinkList):
        raise ValueError("Unsupported operation car")
    return x.car()


def cdr(x):
    if not isinstance(x, LinkList):
        raise ValueError("Unsupported operation cdr")
    return x.cdr()
