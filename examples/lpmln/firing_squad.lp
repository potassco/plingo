u :- &log("0.7/0.3"). 
w :- &log("0.2/0.8").

c :- u.
a :- c.
b :- c.
a :- w.
d :- a.
d :- b.

cs :- u, not do(c1), not do(c0).
as :- cs, not do(a1), not do(a0).
as :- w, not do(a1), not do(a0).
bs :- cs, not do(b1), not do(b0).
ds :- as, not do(d1), not do(d0).
ds :- bs, not do(d1), not do(d0).

cs :- do(c1).
as :- do(a1).
bs :- do(b1).
ds :- do(d1).

