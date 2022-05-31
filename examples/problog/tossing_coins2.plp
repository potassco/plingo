heads(C) :- &problog("0.5"), C=1..2.
two_heads :- heads(1), heads(2).
&query(heads(1)).
&evidence(two_heads, false).
