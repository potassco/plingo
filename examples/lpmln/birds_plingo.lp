bird(X) :- residentBird(X).
bird(X) :- migratoryBird(X).
:- residentBird(X), migratoryBird(X).

{ residentBird(jo) }.
:~ not residentBird(jo). [20000@0,0]

{ migratoryBird(jo) }.
:~ not migratoryBird(jo). [100000@0,0]
