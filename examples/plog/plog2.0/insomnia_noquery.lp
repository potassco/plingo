% sorts

activity(work;sleep).
boolean(true;false).

% attributes

% insomnia: #boolean.
% possible: #activity -> #boolean.
% act: #activity.

% statements

&random { insomnia(B) : boolean(B) }.
&random { act(A) : possible(A,true) }.

possible(X,true) :- not possible(X,false), activity(X).
possible(sleep,false) :- insomnia(true).

&pr { insomnia(true) } = "3/10".
&pr { act(sleep) } = "7/10" :-  insomnia(false). %fixed gamma

%?act = sleep.
%?act = work.

#show insomnia/1.
#show act/1.
#show possible/2.
