(defun location (x y)
  (format nil "l-~A-~A" x y))

(defun road (x1 y1 x2 y2)
  (format nil "(road ~A ~A)" (location x1 y1) (location x2 y2)))

(defun spare (x y)
  (format nil "(spare-in ~A)" (location x y)))

(defun white-layer (x n)
  (format nil "~{~^~A~}~{~^~A~}~{~^~A~}~A~A"
	  (loop :for y :from 1 :to (1- n)
		:collect (road x y x (1+ y)))
	  (when (> x 1)
	    (loop :for y :from 1 :to n :by 2
		  :collect (road (1- x) y x y)))
	  (when (> x 1)
	    (loop :for y :from 1 :to n :by 2
		  :collect (road x y (1- x) (1+ y))))
	  (if (> x 1) (spare x 1) "")
	  (if (> x 1) (spare x n) "")))

(defun black-layer (x n)
  (format nil "~{~^~A~}~{~^~A~}~{~^~A~}"
	  (loop :for y :from 1 :to n
		:collect (road (1- x) y x y))
	  (loop :for y :from 1 :to n
		:collect (road x y (1- x) (1+ y)))
	  (loop :for y :from 1 :to n
		:collect (spare x y))))

(defun objects (n)
  (format nil "~{~^~A ~}- location"
	  (loop :for x :from 1 :to n
		:append (loop :for y :from 1 :to n
			      :collect (location x y)))))

(defun init (n)
  (format nil "(vehicle-at ~A)~{~^~A~}(not-flattire)"
	  (location 1 1)
	  (loop :for y :from n :downto 1
		:and x :from 1
		:collect (if (oddp x)
			     (white-layer x y)
			     (black-layer x y)))))

(defun goal (n)
  (format nil "(and (vehicle-at ~A))" (location 1 n)))

(defun problem (number)
  (let ((n (1+ (* 2 number))))
    (format nil "(define (problem manytireworldprob)
                   (:domain manytireworld)
                   (:objects ~A)
                   (:init ~A)
                   (:goal ~A))"
            (objects n) (init n) (goal n))))
