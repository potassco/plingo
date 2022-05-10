% Sorts
s(1..3).

% Statements
&random {p(S) : s(S)}.

:- p(1).

&query(p(2)).

#show p/1.
