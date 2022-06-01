% Sorts
boolean(true;false).
n(1;2).
m(2;3).

sintersection(X) :- n(X), m(X).
sunion(X) :- m(X).
sunion(X) :- n(X).

ssubtraction(X) :- n(X), not m(X).


% % Attributes
% &random(r1(I)) {p(I,X) : boolean(X)} :- sintersection(I).
% &random(r2(U)) {q(U,X) : boolean(X)} :- sunion(U).
% &random(r3(S)) {r(S,X) : boolean(X)} :- ssubtraction(S).



#show p/2.
#show q/2.
#show r/2.

