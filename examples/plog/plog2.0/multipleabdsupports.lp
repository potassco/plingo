% sorts
% boolean(true;false).

% attributes

% a : #boolean.
% b : #boolean.
% c: #boolean.

% statements
{a}.
{b}.
{c}.

a:- b.
b:- a.
c:- b.
c:- a.

:- not c.

&query(a).


