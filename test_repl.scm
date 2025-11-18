;; PyLisp REPL Test Script

;; Test 1: Simple arithmetic
(display "Test 1: Simple arithmetic")
(newline)
(display (+ 1 2))
(newline)
(display (* 3 4))
(newline)

;; Test 2: Define variables
(display "Test 2: Define variables")
(newline)
(define x 42)
(display x)
(newline)

;; Test 3: Define functions
(display "Test 3: Define functions")
(newline)
(define (square n) (* n n))
(display (square 5))
(newline)

;; Test 4: Factorial (recursion)
(display "Test 4: Factorial")
(newline)
(define (factorial n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))
(display (factorial 5))
(newline)

;; Test 5: Closure
(display "Test 5: Closure")
(newline)
(define (make-adder n)
  (lambda (x) (+ x n)))
(define add5 (make-adder 5))
(display (add5 10))
(newline)

;; Test 6: Tail recursion (sum)
(display "Test 6: Tail recursion sum")
(newline)
(define (sum from to)
  (begin
    (define (iter from to acc)
      (if (> from to)
          acc
          (iter (+ from 1) to (+ acc from))))
    (iter from to 0)))
(display (sum 1 100))
(newline)

(display "All tests completed!")
(newline)
