% Probabilistic facts:
heads1 :- &problog("0.5").
heads2 :- &problog("0.6").

% Rules:
twoHeads :- heads1, heads2.

% Queries:
&query(heads1).
&query(heads2).
&query(twoHeads).
