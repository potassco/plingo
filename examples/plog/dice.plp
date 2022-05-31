% Sorts
dice(d1;d2).
score(1..6).
person(mike;john).

% Regular part
owns(d1,mike).
owns(d2,john).

% Random rules 
&random(r1(D)) { roll(D,X) : score(X) } :- dice(D).

% Probability atoms
&pr(r1(D)) { roll(D,X) } = "1/6"  :- owns(D,john), score(X).
&pr(r1(D)) { roll(D,6) } = "1/4"  :- owns(D,mike).
&pr(r1(D)) { roll(D,X) } = "3/20" :- owns(D,mike), score(X), X != 6.

% Observations and actions
&obs{ roll(d2,1) }.

#show roll/2.
