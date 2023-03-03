prob(0). prob(0,0,0). % to avoid warnings

0.5 ::     hold(A) :- prob(    hold(A)).
0.5 :: not_hold(A) :- prob(not_hold(A)).

   E/(E+1)  :: hold(A) :- prob(0,hold(A),W), E=2.71828182**(W/100000).
1-(E/(E+1)) :: hold(A) :- prob(1,hold(A),W), E=2.71828182**(W/100000).

E/(E+1) :: whold(S,A) :- prob(S,whold(A),W), E=2.71828182**(W/100000).
bot :- prob(0,whold(A),W),     whold(0,A), not hold(A).
bot :- prob(0,whold(A),W), not whold(0,A),     hold(A).
bot :- prob(1,whold(A),W),     whold(1,A),     hold(A).
bot :- prob(1,whold(A),W), not whold(1,A), not hold(A).
