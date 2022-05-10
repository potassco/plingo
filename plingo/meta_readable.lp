%
% Meta-encoding
%

{ _h(A) : _random(E,A)} = 1 :- _random(E,_).

:- not _h(A), _obs(A,true).
:- _h(A),     _obs(A,false).

_h(A) :- _do(A).

_int((P,X)) :- _do((P,X,V)).


%
% Probabilities
%


%
% option = 1
%

% % assigned probability
% :~ _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), _pr(E,(P,X,V),Pr).     [-@log(Pr,_plingo_factor),E]

% :- _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), _pr(E,(P,X,V),Pr),     Pr=0.

% % default numerator
% :~ _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), not _pr(E,(P,X,V),_),
%     Y = #sum { @intpr(Pr),A : _random(E,A), _pr(E,A,Pr) }, @intpr(1)-Y > 0. [-@log(@frac(@intpr(1)-Y,@intpr(1)),_plingo_factor),num,E]

% :- _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), not _pr(E,(P,X,V),_),
%     Y = #sum { @intpr(Pr),A : _random(E,A), _pr(E,A,Pr) },                  @intpr(1)-Y<=0.

% % default denominator
% :~ _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), not _pr(E,(P,X,V),_),
%    M = #count { A : _random(E,A), not _pr(E,A,_) }, M>1.                    [-@log(@frac(1,M),_plingo_factor),den,E]

% :- _random(E,(P,X,_)), _h((P,X,V)), not _int((P,X)), not _pr(E,(P,X,V),_),
%    M = #count { A : _random(E,A), not _pr(E,A,_) },                         M=0.


%
% option = 2
%

_no_int(E)  :- _random(E,(P,X,_)), not _int((P,X)).
_pr(E,Pr)   :- _random(E,A),_h(A), _pr(E,A,Pr).
_default(E) :- _no_int(E), not _pr(E,_).

_numsum(E,Y) :- _default(E), Y = #sum { @intpr(Pr),A : _random(E,A), _pr(E,A,Pr) }.
_densum(E,M) :- _default(E), M = #count{ A : _random(E,A), not _pr(E,A,_) }.

% assigned probability
:~ _pr(E,Pr), _no_int(E).       [   -@log(Pr,_plingo_factor),E]
:- _pr(E,Pr), _no_int(E),           Pr = 0.

% default numerator
:~ _numsum(E,Y), @intpr(1)-Y > 0.   [-@log(@frac(@intpr(1)-Y,@intpr(1)),_plingo_factor),num,E]
:- _numsum(E,Y),                    @intpr(1) - Y <= 0.

% default denominator
:~ _densum(E,M), M > 1.             [-@log(@frac(1,M),_plingo_factor),den,E]
:- _densum(E,M),                    M = 0.


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
