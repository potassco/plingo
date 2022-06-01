% sorts

s(1..3).
s2(1..10).
boolean(true;false).

% attributes
% p: #s,#s -> #boolean.  
% q: #s2-> #boolean.
% a: #s.

% statements

p(X,Y) :- X<Y, s(X), s(Y).
q(1) :- p(1,1).
q(2) :- p(1,2).
q(3) :- p(1,3).
q(4) :- p(2,1).
q(5) :- p(2,2).
q(6) :- p(2,3).
q(7) :- p(3,1).
q(8) :- p(3,2).
q(9) :- p(3,3).
 
% random(a,q).
&random { a(S) : q(S) } :- s(S).

#show a/1.
#show q/1.
#show p/2.
% ?a=2.

&query(a(2)).
