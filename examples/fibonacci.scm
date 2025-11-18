;; Fibonacci sequence examples

;; Recursive version (slow for large n)
(define (fib-recursive n)
  (if (<= n 1)
      n
      (+ (fib-recursive (- n 1))
         (fib-recursive (- n 2)))))

;; Iterative version with tail recursion (fast)
(define (fib-iter n)
  (begin
    (define (iter a b count)
      (if (= count 0)
          a
          (iter b (+ a b) (- count 1))))
    (iter 0 1 n)))

;; Test both versions
(display "Fibonacci using recursion:")
(newline)
(display "fib(0) = ")
(display (fib-recursive 0))
(newline)
(display "fib(5) = ")
(display (fib-recursive 5))
(newline)
(display "fib(10) = ")
(display (fib-recursive 10))
(newline)

(newline)
(display "Fibonacci using iteration (tail recursion):")
(newline)
(display "fib(0) = ")
(display (fib-iter 0))
(newline)
(display "fib(5) = ")
(display (fib-iter 5))
(newline)
(display "fib(10) = ")
(display (fib-iter 10))
(newline)
(display "fib(20) = ")
(display (fib-iter 20))
(newline)
(display "fib(30) = ")
(display (fib-iter 30))
(newline)
