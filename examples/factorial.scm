;; Factorial examples

;; Recursive factorial
(define (factorial-recursive n)
  (if (= n 0)
      1
      (* n (factorial-recursive (- n 1)))))

;; Iterative factorial with tail recursion
(define (factorial-iter n)
  (begin
    (define (iter product counter)
      (if (> counter n)
          product
          (iter (* product counter) (+ counter 1))))
    (iter 1 1)))

;; Test factorial functions
(display "Factorial examples:")
(newline)
(newline)

(display "Recursive version:")
(newline)
(display "0! = ")
(display (factorial-recursive 0))
(newline)
(display "1! = ")
(display (factorial-recursive 1))
(newline)
(display "5! = ")
(display (factorial-recursive 5))
(newline)
(display "10! = ")
(display (factorial-recursive 10))
(newline)

(newline)
(display "Iterative version (tail recursion):")
(newline)
(display "0! = ")
(display (factorial-iter 0))
(newline)
(display "1! = ")
(display (factorial-iter 1))
(newline)
(display "5! = ")
(display (factorial-iter 5))
(newline)
(display "10! = ")
(display (factorial-iter 10))
(newline)
(display "20! = ")
(display (factorial-iter 20))
(newline)
