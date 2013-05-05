import unittest
import parser
import code
import vm
import cStringIO
import runtime
import functools


def compile(source):
    s = cStringIO.StringIO(source)
    lex = parser.Lexer(s)
    visitor = parser.Transform()
    ast = parser.exprs(lex)
    parser.traverse(ast, visitor)
    consts = code.generate(ast)
    return consts


class run_doc(object):
    def __init__(self, results=None):
        self.results = results

    def __call__(self, func):
        results = self.results

        @functools.wraps(func)
        def wrapper(self, *args, **kwds):
            self.run_script(func.__doc__)
            if results:
                self.check_results(results)

        return wrapper


class Lisp(unittest.TestCase):
    def check_results(self, expects):
        self.outputs.seek(0)
        results = [line.strip() for line in self.outputs.readlines()]
        self.assertEqual(len(expects), len(results))
        for result, expect in zip(results, expects):
            self.assertEqual(result, expect)

    def run_script(self, s, debug=False):
        consts = compile(s)

        m = vm.VM(consts, self.env)

        if debug:
            def debug_on():
                m.turn_debug(True)
                return [None]

            def debug_off():
                m.turn_debug(False)
                return [None]

            self.env["debug_on"] = debug_on
            self.env["debug_off"] = debug_off

        m.start()

    def setUp(self):
        outputs = cStringIO.StringIO()

        def display(*args):
            for arg in args:
                outputs.write(str(arg))
            outputs.write("\n")
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

    @run_doc()
    def test_if(self):
        """
        (define (test a) (if (= 0 a) (* 2 3) (+ 2 3)))
        (assert (test 0) 6)
        (assert (test 2) 5)
        """

    @run_doc(["(1 2 3)"])
    def test_vargs(self):
        """
        (define (x . a) (display a))
        (x 1 2 3)
        """

    @run_doc()
    def test_begin(self):
        """
        (define (main)
          (begin
              (define x 1)
              x))
        (assert (main) 1)
        """

    @run_doc(["1", "2", "((1 . 2) 1 . 2)"])
    def test_cons(self):
        """
        (define x (cons 1 2))
        (display (car x))
        (display (cdr x))
        (display (cons x x))
        """

    @run_doc(["3", "7"])
    def test_let(self):
        """
        (define (main)
            (let ((x 1) (y 2))
                (begin
                    (display (+ x y))
                    (lambda () (+ x 1))))
            (let ((x 3) (y 4))
                (begin
                    (display (+ x y))
                    y)))
        (assert (main) 4)
        """

    def test_closure(self):
        s = """
        (define (mul x y) (* x y))
        (define (muln n) (lambda (x) (mul x n)))
        (define mul2 (muln 2))
        (define mul3 (muln 3))
        (debug_on)
        (assert (mul2 2) 4)
        (debug_off)
        (assert (mul3 3) 9)
        (assert (mul3 3.3) (* 3 3.3))
        """
        self.run_script(s, debug=True)

    @run_doc()
    def test_cc(self):
        """
        (define (func x)
            (call/cc
                (lambda (f)
                    (if x (f 2) 3))))
        (assert (func 1) 2)
        (assert (func 0) 3)
        """

    @run_doc(["(4 1 2 3)"])
    def test_uparforvarg(self):
        """
        (define (add . a) (lambda (b) (cons b a)))
        (define add3 (add 1 2 3))
        (display (add3 4))
        """

    @run_doc()
    def test_binops(self):
        """
        (assert 3 (+ 1 2))
        (assert 2 (* 1 2))
        """

    @run_doc()
    def test_py_closure(self):
        """
        (assert (list 1 2 3) (list 1 2 3))
        """

    @run_doc()
    def test_tail_call(self):
        """
        (define (sum from to)
            (begin
                (define (iter from to acc)
                    (if (> from to)
                        acc
                        (iter (+ from 1) to (+ acc from))))
                (iter from to 0)))
        (assert (sum 1 100000) 5000050000)
        """


class LispList(unittest.TestCase):
    def test_sclist2pylist(self):
        from runtime import sclist2pylist, build_list
        x = [1, 2, 3]
        assert x == sclist2pylist(build_list(x))
        x = [1, 2, [3, 4]]
        assert x == sclist2pylist(build_list(x))
        x = [[3, 4], [5, 6]]
        assert x == sclist2pylist(build_list(x))
        x = [1]
        assert x == sclist2pylist(build_list(x))
        x = []
        assert x == sclist2pylist(build_list(x))


if __name__ == '__main__':
    unittest.main()
