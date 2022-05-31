% Sorts
boolean (true;false).

% Attributes
%   smoking : #boolean.
%   tar : #boolean.
%   cancer : #boolean.

% Statements
&random { smoking(B) : boolean(B) }.
&random { tar(B) : boolean(B) }.
&random { cancer(B) : boolean(B) }.

&pr { tar(true) } = "8/10" :- smoking(true).
&pr { tar(true) } = "1/10" :- smoking(false).
&pr { cancer(true) } = "1/100" :- tar(true).
&pr { cancer(true) } = "1/500" :- tar(false).
&pr { smoking(true) } = "3/10".

&do{ cancer(true) }.

&query(smoking(true)).

#show smoking/1.
#show tar/1.
#show cancer/1.
