#lang racket
(require racket/date racket/string racket/uuid racket/hash)
(provide make-sphere sphere-id get-modality add-modality get-modalities
         sphere-entropy set-entropy append-provenance newest-op
         apply-rule pop merge collapse close-sphere boundary-compatible? entropy-increase)

(struct operation (name rule time note) #:transparent)
(struct provenance (origin trace) #:transparent)
(struct sphere (id modalities internal-phi boundary prov entropy type)
  #:mutable #:transparent)

(define (make-sphere type #:modalities [mods (make-hash)]
                    #:internal-phi [phi (make-hash)]
                    #:boundary [boundary '()]
                    #:entropy [entropy 0.0])
  (sphere (uuid) mods phi boundary (provenance #f (list (operation "create" #f (current-inexact-milliseconds) "initial"))) entropy type))

(define (sphere-id s) (sphere-id s))
(define (get-modality s k) (hash-ref (sphere-modalities s) k #f))
(define (get-modalities s) (hash->list (sphere-modalities s)))
(define (sphere-entropy s) (sphere-entropy s))
(define (set-entropy s e) (set-sphere-entropy! s e) s)

(define (now-ms) (current-inexact-milliseconds))
(define (newest-op name rule note) (operation name rule (now-ms) note))

(define (append-provenance s op)
  (let ((p (sphere-prov s)))
    (set-provenance-trace! p (append (provenance-trace p) (list op)))
    s))

(define kappa 0.05)
(define (entropy-increase s s*)
  (let* ((old (map car (get-modalities s)))
         (new (map car (get-modalities s*)))
         (added (filter (lambda (k) (not (member k old))) new)))
    (* kappa (length added))))

(define (boundary-compatible? a b)
  (let ((A (sphere-boundary a)) (B (sphere-boundary b)))
    (cond [(and (null? A) (null? B)) #t]
          [else (ormap (lambda (x) (member x B)) A)])))

(define (apply-rule rule-name impl budget s)
  (with-handlers ([exn:fail? (lambda (e) (values #f (format "rule ~a failed: ~a" rule-name (exn-message e))))])
    (let-values ([(s2 dE cost) (impl s)])
      (if (<= dE budget)
          (begin
            (append-provenance s2 (newest-op "apply-rule" rule-name (format "cost=~a dE=~a" cost dE)))
            (set-sphere-entropy! s2 (+ (sphere-entropy s) dE))
            (values s2 #f))
          (values #f (format "entropy budget exceeded ~a > ~a" dE budget))))))

(define (pop name impl budget s) (apply-rule name impl budget s))

(define (merge name impl budget a b)
  (if (not (boundary-compatible? a b))
      (values #f "boundary compatibility failed")
      (with-handlers ([exn:fail? (lambda (e) (values #f (exn-message e)))])
        (let-values ([(s3 dE cost) (impl a b)])
          (if (<= dE budget)
              (begin
                (append-provenance s3 (newest-op "merge" name (format "cost=~a" cost)))
                (set-sphere-entropy! s3 (+ (sphere-entropy a) (sphere-entropy b) dE))
                (values s3 #f))
              (values #f "merge entropy budget exceeded"))))))

(define (collapse i-min prune s)
  (let ((s2 (prune s)))
    (when (< (sphere-entropy s2) 0) (set-sphere-entropy! s2 0.0))
    s2))

(define (close-sphere rules s)
  (let* ((type (sphere-type s))
         (outs (if (pair? type) (cdr type) '()))
         (missing (filter (lambda (k) (not (hash-has-key? (sphere-modalities s) k))) outs)))
    (let loop ((m missing) (cur s))
      (cond [(null? m) (values cur #f)]
            [else
             (let* ((k (car m))
                    (rs (filter (lambda (r) (equal? (caddr r) k)) rules)))
               (if (null? rs) (values #f "no rule for modality")
                   (let* ((r (car rs))
                          (nm (car r)) (im (cadr r)) (bd (cadddr r)))
                     (let-values ([(s2 e) (apply-rule nm im bd cur)])
                       (if e (values #f e)
                           (loop (cdr m) s2))))))]))))
