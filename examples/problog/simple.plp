% Two ways to write probabilistic facts. Using &log(p/(1-p))
p :- &log("0.6/0.4").
q :- &log("0.3/0.7").

% or using the &problog atom
% p :- &problog("0.6").
% q :- &problog("0.3").

r :- p.
r :- q.

&query(r).
