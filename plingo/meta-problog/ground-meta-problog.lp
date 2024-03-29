%
% Usage:
%   clingo <files> --pre | clingo - --output=reify | clingo - ground-meta-problog.lp --text | \
%   sed -n '/^\(evidence\|query\|show\|prob\|bot\|hold\|cont\)/ p' | sed -e 's:true(0,:hold(:g' -e 's:true(1,:not hold(:g' -e 's:true(2,:not_hold(:g' -e 's:true(3,:not not_hold(:g' | \
%   problog --combine - probs-meta-problog.lp
% where <files> is a plingo program (accepted by clingo)
% with optimize statements at level 0 and only at that level
% where the weights have been multiplied by a factor of 100000.
% This factor can be changed in the probabilistic facts of probs-meta-problog.lp.
%
% Queries should be specified by atoms of predicate query/1.
% Predicate query/1 and the predicates of the atoms that are queried
% must be #shown in <files>.
%
% We allow at most 4 elements per body, it is easy to extend the encoding for longer lengths
:- literal_tuple(B,L), 5 { literal_tuple(B,LL) }.
%


%
% preprocessing
%

literal_tuple(B,0, L,P) :- literal_tuple(B,L), L>=0, P = #count{ LL: literal_tuple(B,LL), LL<=L }.
literal_tuple(B,1,-L,P) :- literal_tuple(B,L), L< 0, P = #count{ LL: literal_tuple(B,LL), LL<=L }.
%
size(B,S) :- literal_tuple(B), S = { literal_tuple(B,L) }.
%
weighted_literal_tuple(B,0, L,W,P) :- rule(H,sum(B,V)), weighted_literal_tuple(B,L,W), L >= 0, P = #count{ LL : weighted_literal_tuple(B,LL,WW), LL<=L }.
weighted_literal_tuple(B,1,-L,W,P) :- rule(H,sum(B,V)), weighted_literal_tuple(B,L,W), L <  0, P = #count{ LL : weighted_literal_tuple(B,LL,WW), LL<=L }.


%
% constraints, facts, open atoms, easy atoms, normal rules, weight rules, choice rules and neg atoms
%
 constraint(B) :- rule(disjunction(H),normal(B)), 0 = { atom_tuple(H,A) }.
       fact(A) :- rule(disjunction(H),normal(B)), atom_tuple(H,A), size(B,0).
       open(A) :- rule(     choice(H),normal(B)), atom_tuple(H,A), size(B,0), not fact(A).
       easy(A) :- fact(A).
       easy(A) :- open(A).
   normal(A,B) :- rule(disjunction(H),normal(B)), atom_tuple(H,A), not easy(A),          not constraint(B).
  onormal(A,B) :- rule(disjunction(H),normal(B)), atom_tuple(H,A), not fact(A), open(A), not constraint(B).
 weight(A,B,W) :- rule(disjunction(H), sum(B,W)), atom_tuple(H,A), not easy(A).
oweight(A,B,W) :- rule(disjunction(H), sum(B,W)), atom_tuple(H,A), not fact(A), open(A).
   choice(A,B) :- rule(     choice(H),normal(B)), atom_tuple(H,A), not easy(A),          not constraint(B).
        neg(A) :- choice(A,B).


%
% dependencies to infer other neg(A)
%

dep(S,A,H) :- normal(H,B),            literal_tuple(B,S,A,P).
dep(S,A,H) :- choice(H,B),            literal_tuple(B,S,A,P).
dep(S,A,H) :- weight(H,B,W), weighted_literal_tuple(B,S,A,V,P).
%
tr(S,A,B) :- dep(S,A,B).
tr(0,A,B) :- dep(0,A,C), tr(0,C,B).
tr(1,A,B) :- dep(1,A,C), tr(X,C,B).
tr(1,A,B) :- dep(X,A,C), tr(1,C,B).
%
neg(A):- tr(1,A,A), not easy(A).


%
% nliteral_tuple(B,S,A,P) and nweighted_literal_tuple(B,S,A,X,P)
%
nliteral_tuple(B,S,A,P) :- literal_tuple(B,S,A,P), S != 1.
nliteral_tuple(B,S,A,P) :- literal_tuple(B,S,A,P), S  = 1, not neg(A).
nliteral_tuple(B,2,A,P) :- literal_tuple(B,S,A,P), S  = 1,     neg(A).
%
nweighted_literal_tuple(B,S,A,X,P) :- weighted_literal_tuple(B,S,A,X,P), S != 1.
nweighted_literal_tuple(B,S,A,X,P) :- weighted_literal_tuple(B,S,A,X,P), S  = 1, not neg(A).
nweighted_literal_tuple(B,2,A,X,P) :- weighted_literal_tuple(B,S,A,X,P), S  = 1,     neg(A).


%
% true(S,A)
%

true(0,A) :-         hold(A).
true(1,A) :-     not hold(A), atom_tuple(H,A).
true(2,A) :-     not_hold(A).
true(3,A) :- not not_hold(A), neg(A).


%
% neg(A)
%
{not_hold(A)} :- neg(A).
bot :-     not_hold(A),     hold(A).
bot :- not not_hold(A), not hold(A), neg(A).
prob(not_hold(A)) :- neg(A).


%
% constraint
%
bot     :- constraint(B), size(B,0).
bot     :- constraint(B), size(B,1),
           literal_tuple(B,S1,A1,1), true(S1,A1).
bot     :- constraint(B), size(B,2),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2).
bot     :- constraint(B), size(B,3),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2),
           literal_tuple(B,S3,A3,3), true(S3,A3).
bot     :- constraint(B), size(B,4),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2),
           literal_tuple(B,S3,A3,3), true(S3,A3),
           literal_tuple(B,S4,A4,4), true(S4,A4).
% ... 5 =  { ... }


%
% weight rules
%
    weight(B,W) :-  weight(A,B,V), W = #max{ WW : weight(AA,B,WW); WW : oweight(AA,B,WW) }.
    weight(B,W) :- oweight(A,B,V), W = #max{ WW : weight(AA,B,WW); WW : oweight(AA,B,WW) }.
cont(B,P+1,  0) :-   weight(B,W), P = { weighted_literal_tuple(B,L,V) }.
cont(B,P-1,  V) :-   weight(B,W), cont(B,P,V), P>1.
cont(B,P-1,X+V) :-   weight(B,W), cont(B,P,V), P>1, nweighted_literal_tuple(B,S,A,X,P-1), true(S,A), V<W.
%
hold(A) :-  weight(A,B,W), cont(B,1,V), V >= W.
    bot :- oweight(A,B,W), cont(B,1,V), V >= W, true(1,A).


%
% normal
%
hold(A) :- normal(A,B), size(B,1),
           nliteral_tuple(B,S1,A1,1), true(S1,A1).
hold(A) :- normal(A,B), size(B,2),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2).
hold(A) :- normal(A,B), size(B,3),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2),
           nliteral_tuple(B,S3,A3,3), true(S3,A3).
hold(A) :- normal(A,B), size(B,4),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2),
           nliteral_tuple(B,S3,A3,3), true(S3,A3),
           nliteral_tuple(B,S4,A4,4), true(S4,A4).
% ... 5 =  { ... }


%
% onormal
%
bot :- onormal(A,B), size(B,1),
       literal_tuple(B,S1,A1,1), true(S1,A1), true(1,A).
bot :- onormal(A,B), size(B,2),
       literal_tuple(B,S1,A1,1), true(S1,A1),
       literal_tuple(B,S2,A2,2), true(S2,A2), true(1,A).
bot :- onormal(A,B), size(B,3),
       literal_tuple(B,S1,A1,1), true(S1,A1),
       literal_tuple(B,S2,A2,2), true(S2,A2),
       literal_tuple(B,S3,A3,3), true(S3,A3), true(1,A).
bot :- onormal(A,B), size(B,4),
       literal_tuple(B,S1,A1,1), true(S1,A1),
       literal_tuple(B,S2,A2,2), true(S2,A2),
       literal_tuple(B,S3,A3,3), true(S3,A3),
       literal_tuple(B,S4,A4,4), true(S4,A4), true(1,A).
% ... 5 =  { ... }


%
% fact
%
hold(|L|) :- fact(|L|),          literal_tuple(B,L  ).
hold(|L|) :- fact(|L|), weighted_literal_tuple(B,L,W).


%
% choice(A,B)
%
hold(A) :- choice(A,B), size(B,1),
           nliteral_tuple(B,S1,A1,1), true(S1,A1), true(3,A).
hold(A) :- choice(A,B), size(B,2),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2), true(3,A).
hold(A) :- choice(A,B), size(B,3),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2),
           nliteral_tuple(B,S3,A3,3), true(S3,A3), true(3,A).
hold(A) :- choice(A,B), size(B,4),
           nliteral_tuple(B,S1,A1,1), true(S1,A1),
           nliteral_tuple(B,S2,A2,2), true(S2,A2),
           nliteral_tuple(B,S3,A3,3), true(S3,A3),
           nliteral_tuple(B,S4,A4,4), true(S4,A4), true(3,A).
% ... 5 =  { ... }


%
% open(A)
%
    {hold(A)} :- open(A).
    block(A)  :- prob(hold(A),W).
prob(hold(A)) :- open(A), not block(A).


%
% minimize
%
min(A,W) :- minimize(0,B), weighted_literal_tuple(B,L,WW), A = |L|,
            W = #sum{ -W1,0 : weighted_literal_tuple(B, A,W1);
                       W2,1 : weighted_literal_tuple(B,-A,W2)}.
%
prob( hold(A),W) :- min(A,W),     open(A).
prob(whold(A),W) :- min(A,W), not open(A).


%
% show
%
show(T) :- output(T,B), size(B,0).
show(T) :- output(T,B), size(B,1),
           literal_tuple(B,S1,A1,1), true(S1,A1).
show(T) :- output(T,B), size(B,2),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2).
show(T) :- output(T,B), size(B,3),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2),
           literal_tuple(B,S3,A3,3), true(S3,A3).
show(T) :- output(T,B), size(B,4),
           literal_tuple(B,S1,A1,1), true(S1,A1),
           literal_tuple(B,S2,A2,2), true(S2,A2),
           literal_tuple(B,S3,A3,3), true(S3,A3),
           literal_tuple(B,S4,A4,4), true(S4,A4).
% ... 5 =  { ... }


%
% evidence and query
%
evidence(bot,false) :- neg(A).
evidence(bot,false) :- constraint(B).
evidence(bot,false) :- onormal(A,B).
evidence(bot,false) :- oweight(A,B,W).
evidence(bot,false) :- prob(A,W).
query(show(T)) :- show(query(T)).

%
% defined predicates
%
#defined literal_tuple/1.
#defined literal_tuple/2.
#defined rule/2.
#defined atom_tuple/2.
#defined weighted_literal_tuple/3.
#defined scc/2.
