{burglary}.
:~not burglary.[-219722@0,0,()]

{earthquake}.
:~not earthquake.[-138629@0,1,()]

{hears_alarm(mary)}.
{hears_alarm(john)}.
:~not hears_alarm(mary).[84729@0,2,(mary,)]
:~not hears_alarm(john).[84729@0,2,(john,)]

alarm :- burglary. 
alarm :- earthquake.
calls(X) :- alarm, hears_alarm(X).

person(mary).
person(john).

% Evidence that alarm has (been observed) to be true
:- not alarm.
