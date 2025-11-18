;; Closure examples - demonstrating lexical scoping

;; Example 1: Simple adder closure
(display "Example 1: Adder closure")
(newline)

(define (make-adder n)
  (lambda (x) (+ x n)))

(define add5 (make-adder 5))
(define add10 (make-adder 10))

(display "add5(3) = ")
(display (add5 3))
(newline)

(display "add10(3) = ")
(display (add10 3))
(newline)

;; Example 2: Multiplier factory
(newline)
(display "Example 2: Multiplier factory")
(newline)

(define (make-multiplier n)
  (lambda (x) (* x n)))

(define double (make-multiplier 2))
(define triple (make-multiplier 3))

(display "double(5) = ")
(display (double 5))
(newline)

(display "triple(5) = ")
(display (triple 5))
(newline)

;; Example 3: Nested closures
(newline)
(display "Example 3: Nested closures")
(newline)

(define (make-power)
  (lambda (base)
    (lambda (exp)
      (begin
        (define (power-iter result count)
          (if (= count 0)
              result
              (power-iter (* result base) (- count 1))))
        (power-iter 1 exp)))))

(define power (make-power))
(define power-of-2 (power 2))
(define power-of-3 (power 3))

(display "2^4 = ")
(display (power-of-2 4))
(newline)

(display "3^3 = ")
(display (power-of-3 3))
(newline)

(display "All closure examples completed!")
(newline)
