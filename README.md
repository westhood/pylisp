# PyLisp: A simple Lisp Implementation in Python

---

## Description ##

The syntax used in PyList is similar to the syntax of scheme in [SICP](http://mitpress.mit.edu/sicp/). You can regard the project as a exercise after learning Chapter 4 and 5 of [SCIP](http://mitpress.mit.edu/sicp/).

## Example ##
1. A Loop to sum integers

    ```
    (define (sum from to)
    (begin
        (define (iter from to acc)
            (if (> from to)
                acc
                (iter (+ from 1) to (+ acc from))))
        (iter from to 0)))
    (display (sum 1 100000))
    ```
2. Make a closure

    ```
    (define (mul x y) (* x y))
    (define (muln n) (lambda (x) (mul x n)))
    (define mul2 (muln 2))
    (define mul3 (muln 3))
    (assert (mul2 2) 4)
    (assert (mul3 3) 9)
    (assert (mul3 3.3) (* 3 3.3))
    ```

## Complete Features ##

* Basic lisp forms like `let`, `lambda`, `if`, `quote` etc.
* Source file will be compiled to VM instructions. No bytecode format for instructions yet. 
* Instruction will be executed by a stacked based virtual machine.
* Lexical scoping (aka Closure).
* Tail call optimize.
* A very inefficient implementation of call/cc (removed in master branch)


## TODO ##

* Bytecode format.
* Marco system in like common lisp.
* RELP.
* A register based virtual machine.