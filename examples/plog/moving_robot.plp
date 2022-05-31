% Sorts
time(0;1).
rooms(r0;r1;r2).

% Regular part
in(1,R) :- go_in(R), not ab.
ab :- break.

in(1,R) :- in(0,R), not -in(1,R).
-in(1,R) :- -in(0,R), not in(1,R), rooms(R).

open(R) :- not -open(R), rooms(R).

% Random rules
&random { in(1,R) : open(R) } :- go_in(_), break.

% Additional rules
#const x = 0.
go_in(r0) :- x > 0.
break :- x > 1.
&pr { in(1,R) } = "1/2" :- go_in(R), break, x = 3.

#show in/2.
