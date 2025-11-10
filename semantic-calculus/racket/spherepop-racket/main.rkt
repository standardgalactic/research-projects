#lang racket
(require "core.rkt" "rules.rkt" "policy.rkt" racket/format)

(define stype '(text proof audio))
(define s1 (make-sphere stype #:entropy 0 #:boundary '("math")))
(hash-set! (sphere-modalities s1) 'text "Primes are infinite.")
(define s2 (make-sphere stype #:entropy 0 #:boundary '("math")))
(hash-set! (sphere-modalities s2) 'text "Euclid proved infinitude of primes.")

(let-values ([(s1p e1) (pop 'pf text->proof 0.05 s1)])
  (unless e1
    (define rules (list (list 'pf text->proof 'proof 0.05)
                        (list 'au text->audio 'audio 0.02)))
    (let-values ([(s1c e2) (close-sphere rules s1p)])
      (unless e2
        (let-values ([(s3 e3) (merge 'mg simple-merge-impl 0.1 s1c s2)])
          (unless e3
            (printf "ok merged entropy=~a
" (sphere-entropy s3))))))))
