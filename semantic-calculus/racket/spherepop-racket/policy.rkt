#lang racket
(require "core.rkt" "rules.rkt" racket/list)
(provide policy-greedy-select apply-policies)

(struct policy (name impl budget cost produces) #:transparent)

(define (policy-greedy-select B ps)
  (let ((ps2 (sort ps (lambda (a b) (< (policy-cost a) (policy-cost b))))))
    (let loop ((b B) (xs ps2) (acc '()))
      (cond [(null? xs) (reverse acc)]
            [(<= b 0) (reverse acc)]
            [else (let ((p (car xs)))
                    (if (<= (policy-cost p) b)
                        (loop (- b (policy-cost p)) (cdr xs) (cons p acc))
                        (loop b (cdr xs) acc)))]))))

(define (apply-policies s ps)
  (let loop ((cur s) (xs ps) (errs '()))
    (cond [(null? xs) (values cur (reverse errs))]
          [else (let ((p (car xs)))
                  (let-values ([(s2 e) (apply-rule (policy-name p) (policy-impl p) (policy-budget p) cur)])
                    (if e (loop cur (cdr xs) (cons e errs))
                        (loop s2 (cdr xs) errs))))])))
