%
% Usage:
%   clingo <files> --output=reify | problog --combine - meta-problog.lp
% where <files> is a plingo program with optimize statements
% at level 0 and only at that level
%

:- use_module(library(aggregate)).


%
% preprocessing
%

literal_tuple((B,0,A),length<LL>) :- literal_tuple(B,L), L>=0, A is abs(L), literal_tuple(B,LL),  LL >= 0, LL=<L.
literal_tuple((B,1,A),length<LL>) :- literal_tuple(B,L), L< 0, A is abs(L), literal_tuple(B,LL),  LL <  0, LL>=L.
%
weighted_literal_tuple((B,0,A,W),length<LL>) :- weighted_literal_tuple(B,L,W), L >= 0, A is abs(L), weighted_literal_tuple(B,LL,WW), LL=<L.
weighted_literal_tuple((B,1,A,W),length<LL>) :- weighted_literal_tuple(B,L,W), L <  0, A is abs(L), weighted_literal_tuple(B,LL,WW), LL=<L.


%
% constraints, weight rules, normal rules, facts, choice rules, simple choices
%

not_constraint(H,B) :- rule(disjunction(H),normal(B)), atom_tuple(H,A).
    constraint(  B) :- rule(disjunction(H),normal(B)), not not_constraint(H,B).
%
weight(A,B,V) :- rule(disjunction(H), sum(B,V)), atom_tuple(H,A).
  normal(A,B) :- rule(disjunction(H),normal(B)), atom_tuple(H,A), literal_tuple(B,L), not constraint(B).
      fact(A) :- rule(disjunction(H),normal(B)), atom_tuple(H,A),    not normal(A,B), not constraint(B).
  choice(A,B) :- rule(     choice(H),normal(B)), atom_tuple(H,A), literal_tuple(B,L), not constraint(B).
  choice(A  ) :- rule(     choice(H),normal(B)), atom_tuple(H,A),    not choice(A,B), not constraint(B).
      easy(A) :-   fact(A).
      easy(A) :- choice(A).
       neg(A) :- choice(A,B), not easy(A).


%
% dependencies to infer other neg(A)
%

dep(0,A,H) :- normal(H,B), literal_tuple(B,L), L>=0, A is abs(L).
dep(1,A,H) :- normal(H,B), literal_tuple(B,L), L< 0, A is abs(L).
dep(0,A,H) :- choice(H,B), literal_tuple(B,L), L>=0, A is abs(L).
dep(1,A,H) :- choice(H,B), literal_tuple(B,L), L< 0, A is abs(L).
dep(0,A,H) :- weight(H,B,_), weighted_literal_tuple(B,L,_), L>=0, A is abs(L).
dep(1,A,H) :- weight(H,B,_), weighted_literal_tuple(B,L,_), L< 0, A is abs(L).
%
% simpler but slower (why?)
% dep(S,A,H) :- normal(H,B),            literal_tuple((B,S,A),_).
% dep(S,A,H) :- choice(H,B),            literal_tuple((B,S,A),_).
% dep(S,A,H) :- weight(H,B,_), weighted_literal_tuple((B,S,A,_),_).
%
tr(S,A,B) :- dep(S,A,B).
tr(0,A,B) :- dep(0,A,C), tr(0,C,B).
tr(1,A,B) :- dep(1,A,C), tr(X,C,B).
tr(1,A,B) :- dep(X,A,C), tr(1,C,B).
%
neg(A):- tr(1,A,A), not easy(A).


%
% hold(Sign,Atom)
%
hold(0,A) :-                 hold(A).
hold(1,A) :-     neg(A), not_hold(A).
hold(1,A) :- not neg(A), not hold(A).


%
% count(Body,1,Value)
%
cont(B,P,V) :-           weighted_literal_tuple((B,S,A,W),P), W >= V, hold(S,A).
cont(B,P,V) :- Q is P+1, weighted_literal_tuple((B,S,A,W),P), weighted_literal_tuple((B,_,_,_),Q), hold(S,A), X is V-W, cont(B,Q,X).
cont(B,P,V) :- Q is P+1,                                      weighted_literal_tuple((B,_,_,_),Q),                      cont(B,Q,V).


%
% conjunction
%
conjunction(B,S,P) :- not literal_tuple((B,S,_),P).
conjunction(B,S,P) :-     literal_tuple((B,S,A),P), hold(S,A), Q is P+1, conjunction(B,S,Q).
%
conjunction(B) :- conjunction(B,0,1), conjunction(B,1,1).


%
% rules
%

% facts
hold(A) :- fact(A).

% simple choices
0.5 :: hold(A) :- choice(A), not fact(A).

% normal rules
hold(A) :- normal(A,B), not easy(A), conjunction(B).
    bot :- normal(A,B),   choice(A), conjunction(B), not hold(A). % translate to constraint if A is open

% choice rules
hold(A) :- choice(A,B), not easy(A), conjunction(B), not not_hold(A).% {a} :- B. is a :- B, not not B.

% weight rules
hold(A) :- weight(A,B,V), cont(B,1,V).

% constraints
    bot :- constraint(B), conjunction(B).

% show
query(prob(T)) :- output(query(T),B), conjunction(B).
      prob(T)  :- query(prob(T)), output(T,B), conjunction(B).

% bot is false
evidence(bot,false).


%
% negation
%
0.5 :: not_hold(L) :- neg(L).
%
bot :- neg(L),     not_hold(L),     hold(L).
bot :- neg(L), not not_hold(L), not hold(L).


%
% weights
%
E/(E+1) :: hold_weight(S,A,W) :- minimize(0,B), weighted_literal_tuple((B,S,A,W),_), E=2.71828182**(W/100000).
bot :- minimize(0,B), weighted_literal_tuple((B,0,A,W),_),     hold_weight(0,A,W), not hold(A).
bot :- minimize(0,B), weighted_literal_tuple((B,0,A,W),_), not hold_weight(0,A,W),     hold(A).
bot :- minimize(0,B), weighted_literal_tuple((B,1,A,W),_), not hold_weight(1,A,W), not hold(A).
bot :- minimize(0,B), weighted_literal_tuple((B,1,A,W),_),     hold_weight(1,A,W),     hold(A).
