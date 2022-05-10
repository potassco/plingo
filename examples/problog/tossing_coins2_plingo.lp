{ heads(C) } :- C=1..2.
:~ not heads(C), C=1..2. [0@0,0,(C,)]

two_heads :- heads(1), heads(2).
&query(heads(1)).

:- two_heads.

