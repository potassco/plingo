% Sorts
door(1..3).

% Regular part
-canopen(D) :- selected(D).
-canopen(D) :- prize(D).
canopen(D)  :- not -canopen(D), door(D).

% Random selection rules
&random { prize(D)    : door(D)    }.
&random { selected(D) : door(D)    }.
&random { open(D)     : canopen(D) }.

% Observations and actions
&obs { selected(1) }.
&obs { open(2)     }.
&obs { prize(2)    } = false.

#show prize/1.
#show selected/1.
#show open/1.
