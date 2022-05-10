% Sorts
result(true;false).

% Regular part
{action(a;b)} = 1.

% Random rules 
&random(r) { success(B) : result(B) }.

% Probability atoms
&pr(r) { success(true) } = "0.7" :- action(a).
&pr(r) { success(false) } = "0.3" :- action(a).
&pr(r) { success(true) } = "0.2" :- action(b).
&pr(r) { success(false) } = "0.8" :- action(b).

#show success/1.
#show action/1.

