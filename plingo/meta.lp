%
% Meta-encoding
%

{ _plingo_h(A) : _plingo_random(E,A)} = 1 :- _plingo_random(E,_).

:- not _plingo_h(A), _plingo_obs(A,true).
:- _plingo_h(A),     _plingo_obs(A,false).

_plingo_h(A) :- _plingo_do(A).

_plingo_int((P,X)) :- _plingo_do((P,X,V)).

#defined _plingo_obs/2.
#defined _plingo_do/1.
#defined _plingo_pr/3.

%
% Probabilities
%

_plingo_no_int(E)  :- _plingo_random(E,(P,X,_)), not _plingo_int((P,X)).
_plingo_pr(E,Pr)   :- _plingo_random(E,A),_plingo_h(A), _plingo_pr(E,A,Pr).
_plingo_default(E) :- _plingo_no_int(E), not _plingo_pr(E,_).

_plingo_numsum(E,Y) :- _plingo_default(E), Y = #sum { @intpr(Pr),A : _plingo_random(E,A), _plingo_pr(E,A,Pr) }.
_plingo_densum(E,M) :- _plingo_default(E), M = #count{ A : _plingo_random(E,A), not _plingo_pr(E,A,_) }.

% assigned probability
:~ _plingo_pr(E,Pr), _plingo_no_int(E).       [   -@log(Pr,_plingo_factor),E]
:- _plingo_pr(E,Pr), _plingo_no_int(E),           Pr = 0.

% default numerator
:~ _plingo_numsum(E,Y), @intpr(1)-Y > 0.   [-@log(@frac(@intpr(1)-Y,@intpr(1)),_plingo_factor),num,E]
:- _plingo_numsum(E,Y),                    @intpr(1) - Y <= 0.

% default denominator
:~ _plingo_densum(E,M), M > 1.             [-@log(@frac(1,M),_plingo_factor),den,E]
:- _plingo_densum(E,M),                    M = 0.


#script (python)
from clingo import Number, String
from math import log as mathlog

def log(a, factor):
    factor = factor.number
    ln = mathlog(float(eval(a.string)))
    weight = Number(int(ln * (10**factor)))
    return weight

def frac(n,d):
    return String(f'{n.number}/{d.number}')

def intpr(a):
    factor = 10**6
    if str(a.type) == 'SymbolType.String':
        return Number(int(float(eval(a.string))*factor))
    elif str(a.type) == 'SymbolType.Number':
        return Number(a.number*factor)
#end.
