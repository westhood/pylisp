# pylisp: A simple Lisp Implementation in Python

## Description ##

The syntax used in PyList is similar to the syntax of scheme in [SICP](http://mitpress.mit.edu/sicp/). You can regard the project as a exercise after learning Chapter 4 and 5 of [SICP](http://mitpress.mit.edu/sicp/).

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
* **REPL (Read-Eval-Print Loop)** - Interactive environment for testing and running Lisp code.
* A very inefficient implementation of call/cc (removed in master branch)

## Using the REPL ##

### Interactive Mode

Start the REPL in interactive mode:

```bash
python repl.py
```

### Execute a File

Run a Lisp script file:

```bash
python repl.py -f your_script.scm
```

### Debug Mode

Enable debug mode to see VM instructions:

```bash
python repl.py -d
python repl.py -f script.scm -d
```

### REPL Features

- Multi-line input with automatic parenthesis balancing
- Built-in functions: `display`, `newline`, `list`, `length`, etc.
- Special commands: `:help`, `:quit`, `:debug on/off`
- Error handling without crashing
- Command history (if terminal supports)

For detailed usage, see [REPL_GUIDE.md](REPL_GUIDE.md)

### Example Programs

Check out the `examples/` directory for sample programs:
- `examples/fibonacci.scm` - Fibonacci sequence (recursive and iterative)
- `examples/factorial.scm` - Factorial computation
- `examples/closures.scm` - Closure demonstrations

## Running Tests ##

Run the test suite:

```bash
python tests.py
```

## TODO ##

* Bytecode format.
* Marco system in like common lisp.
* ~~REPL~~ ✓ (Completed!)
* A register based virtual machine.