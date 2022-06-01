#const n = 1.

% sorts
a(a;b;c).
%#f =  f(#a(X),#a(Y),#a(Z)):   X< Y & X>Z | Z>Y.
boolean(true;false).

% attributes
% x: #a -> #boolean.
% y: #a -> #boolean.
% p: #boolean -> #boolean.

% statements
 
y(a,true).
p(true,true) :- y(a,true).
p(false,true).
&random { x(X,B) : p(B,true) } :- y(X,true), a(X).

&pr { x(a,true) } = "3/10" :- y(a,true).

&query(x(a,true)).

#show x/2.
#show y/2.
