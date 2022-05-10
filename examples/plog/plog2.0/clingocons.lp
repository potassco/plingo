% Sorts
boolean(true;false).

% Statements
&random {a(B) : boolean(B)}.
&random {b(B) : boolean(B)}.

g:- not h,a(true).
h:- not g,a(true).
q:- a(true).


x.
-x :- b(true), h.
-x :- b(false), h. 

&query(q).

#show g/0.
#show h/0.
#show x/0.
#show a/1.
#show b/1.
