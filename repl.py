#!/usr/bin/env python
"""
PyLisp REPL (Read-Eval-Print Loop)

A interactive environment for the PyLisp interpreter.
"""

import sys
import traceback
from parser import Parser, Transform, traverse
import code
import vm
import runtime


class REPL:
    """Interactive REPL for PyLisp"""

    def __init__(self, debug=False):
        self.env = self._create_environment()
        self.debug = debug
        self.prompt = "pylisp> "
        self.continuation_prompt = "....... "

    def _create_environment(self):
        """Create the global environment with built-in functions"""
        env = {}

        # Display function
        def display(*args):
            for arg in args:
                print(arg, end='')
            print()
            return [None]

        # Newline function
        def newline():
            print()
            return [None]

        # List constructor
        def new_list(*args):
            return [runtime.build_list(args)]

        # Length function
        def length(lst):
            count = 0
            while lst is not None:
                if isinstance(lst, runtime.LinkList):
                    lst = lst.cdr()
                    count += 1
                else:
                    break
            return [count]

        # Type checking functions
        def is_null(obj):
            return [obj is None]

        def is_pair(obj):
            return [isinstance(obj, runtime.LinkList)]

        def is_number(obj):
            return [isinstance(obj, (int, float))]

        def is_string(obj):
            return [isinstance(obj, str)]

        # Arithmetic functions
        def modulo(a, b):
            return [a % b]

        def quotient(a, b):
            return [a // b]

        def remainder(a, b):
            return [a % b]

        # Comparison functions
        def less_than(a, b):
            return [a < b]

        def less_equal(a, b):
            return [a <= b]

        def greater_equal(a, b):
            return [a >= b]

        # Logic functions
        def not_op(a):
            return [not a]

        # Register built-in functions
        env['display'] = display
        env['newline'] = newline
        env['list'] = new_list
        env['length'] = length
        env['null?'] = is_null
        env['pair?'] = is_pair
        env['number?'] = is_number
        env['string?'] = is_string
        env['modulo'] = modulo
        env['quotient'] = quotient
        env['remainder'] = remainder
        env['<'] = less_than
        env['<='] = less_equal
        env['>='] = greater_equal
        env['not'] = not_op

        return env

    def _is_balanced(self, text):
        """Check if parentheses are balanced"""
        count = 0
        in_string = False
        escape = False

        for char in text:
            if escape:
                escape = False
                continue

            if char == '\\':
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:
                if char == '(':
                    count += 1
                elif char == ')':
                    count -= 1
                    if count < 0:
                        return False

        return count == 0

    def _read_expression(self):
        """Read a complete expression from user input"""
        lines = []
        prompt = self.prompt

        while True:
            try:
                line = input(prompt)
            except EOFError:
                return None
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                return ""

            # Handle special commands
            line_stripped = line.strip()
            if not lines:  # Only check on first line
                if line_stripped in [':quit', ':exit', 'exit', 'quit']:
                    return None
                if line_stripped in [':help', 'help']:
                    self._show_help()
                    return ""
                if line_stripped == ':debug on':
                    self.debug = True
                    print("Debug mode enabled")
                    return ""
                if line_stripped == ':debug off':
                    self.debug = False
                    print("Debug mode disabled")
                    return ""

            lines.append(line)
            text = '\n'.join(lines)

            # Skip empty input
            if not text.strip():
                return ""

            # Check if expression is complete
            if self._is_balanced(text):
                return text

            prompt = self.continuation_prompt

    def _eval(self, source):
        """Compile and evaluate source code"""
        # Parse
        p = Parser(source)
        visitor = Transform()
        ast = p.exprs()

        # Transform AST
        traverse(ast, visitor)

        # Generate code
        consts = code.generate(ast)

        # Execute in VM
        machine = vm.VM(consts, self.env, debug=self.debug)
        machine.start()

        # Get the result from the last expression
        # For REPL, we want to return the last value on the stack
        return None

    def _show_help(self):
        """Show help information"""
        help_text = """
PyLisp REPL - Interactive Lisp Environment

Special Commands:
  :help, help        - Show this help message
  :quit, :exit       - Exit the REPL
  exit, quit         - Exit the REPL
  :debug on          - Enable debug mode (show VM instructions)
  :debug off         - Disable debug mode

Built-in Functions:
  Arithmetic: +, -, *, /, modulo, quotient, remainder
  Comparison: =, >, <, <=, >=
  List operations: cons, car, cdr, list, length
  Type predicates: null?, pair?, number?, string?
  I/O: display, newline
  Logic: not

Special Forms:
  define, lambda, let, if, begin, quote

Examples:
  (define x 42)
  (define (square n) (* n n))
  (square 5)
  (define (factorial n)
    (if (= n 0)
        1
        (* n (factorial (- n 1)))))
  (factorial 5)

For more information, see README.md
"""
        print(help_text)

    def _show_banner(self):
        """Show welcome banner"""
        banner = """
PyLisp REPL v0.1
Type ':help' for help, ':quit' to exit
"""
        print(banner)

    def run(self):
        """Run the REPL loop"""
        self._show_banner()

        while True:
            try:
                # Read
                source = self._read_expression()

                if source is None:  # EOF or quit command
                    print("\nBye!")
                    break

                if not source.strip():  # Empty input
                    continue

                # Eval
                self._eval(source)

            except Exception as e:
                # Print error without crashing
                print(f"Error: {type(e).__name__}: {e}")
                if self.debug:
                    traceback.print_exc()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='PyLisp REPL')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-f', '--file', type=str,
                        help='Execute a file instead of starting REPL')

    args = parser.parse_args()

    if args.file:
        # Execute file mode
        repl = REPL(debug=args.debug)
        try:
            with open(args.file, 'r') as f:
                source = f.read()
            repl._eval(source)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            if args.debug:
                traceback.print_exc()
            sys.exit(1)
    else:
        # Interactive REPL mode
        repl = REPL(debug=args.debug)
        try:
            repl.run()
        except KeyboardInterrupt:
            print("\n\nBye!")
            sys.exit(0)


if __name__ == '__main__':
    main()
