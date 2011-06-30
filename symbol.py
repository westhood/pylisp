from vm import *

class SymbolException(Exception):pass
class Scope(dict):pass

class SymbolTable(object):
    def __init__(self, generator):
        self.generator = generator
        # we mark the first scope as Global Scope
        self.globalScope = Scope()
        self.globalScope.proto = generator.proto
        self.current = self.globalScope
        self.scopes = []
        self.consts = generator.consts

    def push(self, proto=None):
        scope = Scope()
        if proto:
            scope.proto = proto
            # a new proto, reset index to 0
            self.index = 0
            scope.index = self.index
        else:
            scope.proto = self.current.proto
            self.index += 1
            scope.index = self.index

        self.scopes.append(self.current)
        self.current = scope
        self.proto = self.current.proto
    
    def current_scope(self):
        return self.current

    def pop(self):
        assert not (self.current is self.globalScope)
        old = self.current
        self.current = self.scopes.pop()
        self.proto = self.current.proto
        return old

    def lookup(self, symbol):
        if symbol in self.current:
            return self.current[symbol], self.current
        else:
            for scope in reversed(self.scopes):
                if symbol in scope:
                    return scope[symbol], scope
            return None

    def add(self, symbol, info=None):
        if symbol in self.current:
            exp = SymbolException("symbol '%s' is already defined in current scope.", symbol)
            exp.scopes = self.scopes
            exp.scope = self.current
            raise exp
        else:
            if info:
                self.current[symbol] = info
                return info

            if self.current is self.globalScope:
                index = self.consts.addLiteral(symbol)
                # add symbol in global scope:
                self.current[symbol] = index 
                return "global", index
            else:
                info = self.proto.iLocalvars
                self.current[symbol] = { "local":info }
                self.proto.iLocalvars += 1
                self.proto.adjustMaxLocalvars()
                return "local", info


    def _findSymbol(self, sym):
        ret = self.lookup(sym)
        if ret == None:
            index = self.consts.addLiteral(sym)
            return ("global", index)
        info, scope = ret
        if scope is self.globalScope:
            index = self.consts.addLiteral(sym)
            return ("global", index)

        if scope.proto is self.proto:
            if "varg" in info:
                return ("varg", -1)
            # 'sym' is a local symbol.
            else:
                return ("local", info["local"])

        else:
            # 'sym' is a upvar symbol already.
            if "upvar" in info:
                return ("upvar", info["upvar"])
            # 'sym ' is a local and will become a upvar.
            scopes = []   
            scopes.append(self.current)
            for s in reversed(self.scopes):
                scopes.append(s)
                if s is scope:
                    break

            # get protos for scopes.
            protos = []
            for s in scopes:
                if len(protos) == 0 or (s.proto is not protos[-1]):
                    protos.append(s.proto)

            # remove the proto where symbol is a local.
            top_proto = protos.pop()
            protos.reverse()

            # add upvar in the proto
            if "local" in info:
                protos[0].upvars.append(("local", info["local"]))
            elif "varg" in info:
                protos[0].upvars.append(("varg", -1))

            pre = protos[0]
            for proto in protos[1:]:
                proto.upvars.append(("up", len(pre.upvars) - 1))
                pre = proto

            # add new symbol in scopes list. 
            for s in scopes[:-1]:
                # not for scope will symbol should be a local symbol
                if s.proto is not top_proto:
                    assert sym not in s
                    s[sym] = { "upvar" : len(s.proto.upvars) - 1 }

            return ("upvar", self.current[sym]["upvar"])


    def genLoadSymbol(self, sym):
        type, info = self._findSymbol(sym)
        if type == "global":
            return self.generator.gen((OpLoadGlobal, info))
        elif type == "local":
            return self.generator.gen((OpLoadLocal, info))
        elif type == "varg":
            return self.generator.gen((OpLoadVarg, info))
        elif type == "upvar":
            return self.generator.gen((OpLoadUpvar, info))
        else:
            assert 0 

    def genLoadSymbol(self, sym):
        type, info = self._findSymbol(sym)
        if type == "global":
            return self.generator.gen((OpSetGlobal, info))
        elif type == "local":
            return self.generator.gen((OpSetLocal, info))
        elif type == "varg":
            return self.generator.gen((OpSetVarg, info))
        elif type == "upvar":
            return self.generator.gen((OpSetUpvar, info))
        else:
            assert 0 

    def genLoadSymbol(self, sym):
        ret = self.lookup(sym)
        if ret == None:
            index = self.consts.addLiteral(sym)
            return self.generator.gen((OpLoadGlobal, index))
        info, scope = ret
        if scope is self.globalScope:
            index = self.consts.addLiteral(sym)
            return self.generator.gen((OpLoadGlobal, index))

        if scope.proto is self.proto:
            if "varg" in info:
                return self.generator.gen((OpLoadVarg, -1))
            # 'sym' is a local symbol.
            else:
                return self.generator.gen((OpLoadLocal, info["local"]))

        else:
            # 'sym' is a upvar symbol already.
            if "upvar" in info:
                return self.generator.gen((OpLocalUpvar, info["upvar"]))
            # 'sym ' is a local and will become a upvar.
            scopes = []   
            scopes.append(self.current)
            for s in reversed(self.scopes):
                scopes.append(s)
                if s is scope:
                    break

            # get protos for scopes.
            protos = []
            for s in scopes:
                if len(protos) == 0 or (s.proto is not protos[-1]):
                    protos.append(s.proto)

            # remove the proto where symbol is a local.
            top_proto = protos.pop()
            protos.reverse()

            # add upvar in the proto
            if "local" in info:
                protos[0].upvars.append(("local", info["local"], scope.index))
            elif "varg" in info:
                protos[0].upvars.append(("varg", None, None))

            pre = protos[0]
            for proto in protos[1:]:
                proto.upvars.append(("up", len(pre.upvars) - 1, None))
                pre = proto

            # add new symbol in scopes list. 
            for s in scopes[:-1]:
                # not for scope will symbol should be a local symbol
                if s.proto is not top_proto:
                    assert sym not in s
                    s[sym] = { "upvar" : len(s.proto.upvars) - 1 }

            return self.generator.gen((OpLoadUpvar, self.current[sym]["upvar"]))
