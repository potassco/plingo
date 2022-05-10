burglary :- &problog("0.1").
earthquake :- &problog("0.2").
hears_alarm(X) :- person(X), &problog("0.7").

alarm :- burglary. 
alarm :- earthquake.
calls(X) :- alarm, hears_alarm(X).

person(mary).
person(john).

#show burglary/0.
#show earthquake/0.
#show hears_alarm/1.

&evidence(alarm,true).
% &query(hears_alarm(P)) :-  hears_alarm(P).
&query(burglary).
