prob(0). prob(0,0). % to avoid warnings

0.5 ::     hold(A) :- prob(    hold(A)).
0.5 :: not_hold(A) :- prob(not_hold(A)).

E/(E+1)  :: hold(A) :- prob(hold(A),W), E=2.71828182**(W/100000).

E/(E+1) :: whold(A) :- prob(whold(A),W), E=2.71828182**(W/100000).
bot :- prob(whold(A),W),     whold(A), not hold(A).
bot :- prob(whold(A),W), not whold(A),     hold(A).
