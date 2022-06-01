% Sorts
patch(p1;p2).
boolean(t;f).

% Regular part
found(P,D,f) :- not found(P,D,t), patch(P), day(D).

% Random rules
&random { hidden_in(P) : patch(P) }.
&random { found(P,D,B) : boolean(B) } :- hidden_in(P), look(D,P).

% Probability
&pr { hidden_in(p1) } = "0.8".
&pr { found(P,D,t) } = "0.2" :- patch(P), day(D).

% Bayesian updating per day
#const days = 0.
day(1..days).

% Two assumptions:
% 1. The squirrel looks in the same patch every day
look(D,p1) :- day(D).

% 2. The squirrel has not found the acorns in all past days
&obs { found(p1,D,f) } :- day(D), D < days.

found(P,D) :- found(P,D,t).
#show hidden_in/1.
#show found/2.
