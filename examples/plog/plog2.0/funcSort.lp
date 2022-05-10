% Sorts
n(1..3).
m(1..2).
f(N,M) :- n(N), m(M).
boolean(true;false).

% attributes
% p: #f -> #boolean.

% Statements
p(f(N,M)) :- f(N,M).

#show p/1.
