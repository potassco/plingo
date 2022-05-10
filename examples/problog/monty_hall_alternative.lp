% Based on https://dtai.cs.kuleuven.be/problog/tutorial/various/01_montyhall.html

%*
There is 1/3 chance that I picked a car.
I picked a goat, if I did not pick a car.
There is 1/2 chance that I picked goat1, if I picked a goat.
I picked goat2, if I picked a goat and did not pick goat1.

There is 1/2 chance that goat1 is revealed, if I picked a car.
Goat1 is revealed, if I picked goat2.
There is 1/2 chance that goat2 is revealed, if I picked a car.
Goat2 is revealed, if I picked goat1.

Switching gets me a car, if I picked a goat and a goat was revealed.
Switching gets me a goat, if switching did not get me a car.
*%

picked_car :- &problog("1/3").
picked_goat :- not picked_car.
picked_goat(1):- picked_goat, &problog("1/2").
picked_goat(2) :- picked_goat,  not picked_goat(1).

revealed_goat(1) :- picked_car, &problog("1/2").
revealed_goat(1) :- picked_goat(2).
revealed_goat(2) :- picked_car, &problog("1/2").
revealed_goat(2) :- picked_goat(1).
revealed_goat :- revealed_goat(X).
:- not 1 {revealed_goat(X)} 1.

switched_gets_car :- picked_goat, revealed_goat.
switched_gets_goat :- not switched_gets_car.

&query(switched_gets_car).
&query(switched_gets_goat).
