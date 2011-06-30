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

class TestPyLang(unittest.TestCase):
    def check_results(self, expects):
        self.outputs.seek(0)
        results = [ line.strip() for line in self.outputs.readlines() ]
        self.assertEqual(len(expects), len(results))
        for result, expect in zip(results, expects):
            self.assertEqual(result, expect)

    def setUp(self):
        outputs = cStringIO.StringIO()
        def display(*args):
            for arg in args:
                print >>outputs, arg,
            print >>outputs
            return [None]
        env = {}

        def assertEqual(*args):
            assert len(args) == 2
            self.assertEqual(*args[0:2])
            return [None]

        def newList(*args):
            return [runtime.build_list(args)]

        env["display"] = display
        env["assert"] = assertEqual
        env["list"] = newList
        self.env = env
        self.outputs = outputs

    def test_if(self):
        s = """
        (define (test a) (if (= 0 a) (* 2 3) (+ 2 3)))
        (display (test 0))
        (display (test 2))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["6", "5"])

    def test_vargs(self):
        s = """
        (define (x . a) (display a))
        (x 1 2 3)
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["(1 2 3)"])

    def test_begin(self):
        s = """
        (define (main)
          (begin (define x 1)
              (display x)
              x))
        (main)
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["1"])

    def test_cons(self):
        s = """
        (define x (cons 1 2))
        (display (car x))
        (display (cdr x))
        (display (cons x x))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["1", "2", "((1 . 2) 1 . 2)"])

    def test_let(self):
        s = """ 
        (define (main) 
            (let ((x 1) (y 2))
                (begin 
                    (display (+ x y))
                    (lambda () (+ x 1))))
            (let ((x 3) (y 4))
                (begin 
                    (display (+ x y))
                    y)))
        (display (main)) 
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["3", "7", "4"])

    def test_closure(self):
        s = """
        (define (mul x y) (* x y))
        (define (muln n) (lambda (x) (mul x n)))
        (define mul2 (muln 2))
        (define mul3 (muln 3))
        (display (mul2 2))
        (display (mul3 3))
        (display (mul3 3.3))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["4", "9", "9.9"])

    
    def test_cc(self):
        s = """
        (define (func x)
            (call/cc 
                (lambda (f)
                    (if x (f 2) 3))))
        (assert (func 1) 2)
        (assert  (func 0) 3)
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()

    def test_uparforvarg(self):
        s = """
        (define (add . a) (lambda (b) (cons b a)))
        (define add3 (add 1 2 3))
        (display (add3 4))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        self.check_results(["(4 1 2 3)"])

    def test_binops(self):
        s = """
        (assert 3 (+ 1 2))
        (assert 2 (* 1 2))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()
        print self.outputs.getvalue()
    
    def test_py_closure(self):
        s = """
        (assert (list 1 2 3) (list 1 2 3))
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()

    def test_tail_call(self):

        s = """
        (define (sum from to)
            (begin
                (define (iter from to acc)
                    (if (> from to)
                        acc
                        (iter (+ from 1) to (+ acc from))))
                (iter from to 0)))
        (assert (sum 1 100000) 5000050000)
        """
        consts = compile(s)
        vm.VM(consts, self.env).start()

     
def test():
    s = """
    (define (sum from to)
        (begin
            (define (iter from to acc)
                (if (> from to)
                    acc
                    (iter (+ from 1) to (+ acc from))))
            (iter from to 0)))
    (assert (sum 1 1000) 500500)
    """
    s = """
    (define (main) 
            (let ((x 1) (y 2))
                (begin 
                    (display (+ x y))
                    (lambda () (+ x 1))))
            (let ((x 3) (y 4))
                (begin 
                    (display (+ x y))
                    y)))
    """
 
    def display(*args):
        for arg in args:
            print arg,
        print ""
        return [None]

    def newList(*args):
        ret = runtime.build_list(args)
        return [ret]

    env = {}
    env["display"] = display
    env["list"] = newList 

    s = cStringIO.StringIO(s)
    lex = parser.Lexer(s)
    visitor = parser.Transform()
    ast = parser.exprs(lex)
    parser.traverse(ast, visitor)
    print ast
    consts = code.generate(ast)

    vm.VM(consts, env).start() 

if __name__ == '__main__':
    unittest.main()
