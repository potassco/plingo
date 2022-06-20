from typing import List, Tuple

from clingo import ast
from clingo.ast import AST, ASTSequence


def lit(func: AST) -> AST:
    return ast.Literal(func.location, 0, ast.SymbolicAtom(func))


class ConvertPlog:
    '''
    Provides functions to convert various theory atoms
    used for modeling P-Log.
    '''

    def __get_tuple(self, attr: AST) -> Tuple[AST, AST]:
        loc = attr.location
        attr_name = ast.Function(loc, attr.name, [], False)
        domain_vars, range_var = attr.arguments[:-1], attr.arguments[-1]
        domain_tup = ast.Function(loc, '', domain_vars, False)
        attr_tup = ast.Function(loc, '', [attr_name, domain_tup, range_var],
                                False)
        exp_tup = ast.Function(loc, attr.name, [domain_tup], False)
        return (attr_tup, exp_tup)

    def convert_random(self, ta: AST, body: ASTSequence) -> List[AST]:
        '''
        Input:
            &random(r(D)) { name(D,Y) : range(Y) } :- body(D).
                or if one random rule per attribute
            &random       { name(D,Y) : range(Y) } :- body(D).
        Output:
            Let E = r(D) or E = name(D)

            1. _random(E,(name,D,Y)) :- range(Y), body(D).
            2. _h((name,D,Y)) :- name(D,Y).
            3. name(D,Y) :- _h((name,D,Y)).

        Note:
            We actually prepend _plingo to all of the above
            atoms with underscore to avoid naming conflicts.
        '''
        loc = ta.location
        attr = ta.elements[0].terms[0]
        range = ta.elements[0].condition[0]

        attr_tup, exp_tup = self.__get_tuple(attr)
        if len(ta.term.arguments) != 0:
            exp_tup = ta.term.arguments[0]

        _random = ast.Function(loc, '_plingo_random', [exp_tup, attr_tup],
                               False)

        body.insert(0, range)
        _random_rule = ast.Rule(loc, lit(_random), body)

        hold = ast.Function(loc, '_plingo_h', [attr_tup], False)
        attr = ast.Function(loc, attr.name, [v for v in attr.arguments], False)
        readable_to_meta = ast.Rule(loc, lit(hold), [lit(attr)])
        meta_to_readable = ast.Rule(loc, lit(attr), [lit(hold)])
        return [_random_rule, readable_to_meta, meta_to_readable]

    def convert_pr(self, ta: AST, body: ASTSequence) -> List[AST]:
        '''
        Input:
            &pr(r(D)) { name(D,Y) } = "3/20"  :- body(D,Y).
                or if one random rule per attribute
            &pr        { name(D,Y) } = "3/20"  :- body(D,Y).
        Output:
            Let E = r(D) or E = name(D)
            _pr(E),(name,D,Y),"3/20") :- body(D,Y).
        Note:
            We actually prepend _plingo to all of the above
            atoms with underscore to avoid naming conflicts.
        '''
        loc = ta.location
        attr = ta.elements[0].terms[0]
        prob = ta.guard.term

        attr_tup, exp_tup = self.__get_tuple(attr)
        if len(ta.term.arguments) != 0:
            exp_tup = ta.term.arguments[0]
        _pr = ast.Function(loc, '_plingo_pr', [exp_tup, attr_tup, prob], False)

        _pr_rule = ast.Rule(loc, lit(_pr), body)
        return [_pr_rule]

    def convert_obs(self, ta: AST, body: ASTSequence) -> List[AST]:
        '''
        TODO: No body allowed
        TODO: Should work in general (not just for random attributes)
        Input:
            &obs { name(D,Y) } = bool :- body.
        Output:
             _obs((name,D,Y), bool) :- body.

            bool can be omitted and is true by default
        '''
        loc = ta.location
        attr = ta.elements[0].terms[0]
        attr_tup, _ = self.__get_tuple(attr)
        args = [attr_tup]
        if ta.guard is not None:
            args.append(ta.guard.term)
        else:
            args.append(ast.Function(loc, 'true', [], False))
        _obs = ast.Function(loc, '_plingo_obs', args, False)
        return [ast.Rule(loc, lit(_obs), body)]

    def convert_do(self, ta: AST, body: ASTSequence) -> List[AST]:
        '''
        TODO: No body allowed in &do atoms (new P-Log)
        TODO: Should be able to specify experiment name
            Input:
                &do { name(D,Y) } :- body.
            Output:
                _do((name,D,Y))  :- body.
        '''
        loc = ta.location
        attr = ta.elements[0].terms[0]
        attr_tup, _ = self.__get_tuple(attr)
        args = [attr_tup]

        _do = ast.Function(loc, '_plingo_do', args, False)
        return [ast.Rule(loc, lit(_do), body)]


def get_meta_encoding() -> str:
    '''
    Returns the meta encoding which can be found in plingo/meta.lp.
    '''
    return encoding


encoding = '''
{ _plingo_h(A) : _plingo_random(E,A)} = 1 :- _plingo_random(E,_).

:- not _plingo_h(A), _plingo_obs(A,true).
:- _plingo_h(A),     _plingo_obs(A,false).

_plingo_h(A) :- _plingo_do(A).

_plingo_int((P,X)) :- _plingo_do((P,X,V)).

#defined _plingo_obs/2.
#defined _plingo_do/1.
#defined _plingo_pr/3.

_plingo_no_int(E)  :- _plingo_random(E,(P,X,_)), not _plingo_int((P,X)).
_plingo_pr(E,Pr)   :- _plingo_random(E,A),_plingo_h(A), _plingo_pr(E,A,Pr).
_plingo_default(E) :- _plingo_no_int(E), not _plingo_pr(E,_).

_plingo_numsum(E,Y) :- _plingo_default(E), Y = #sum { @intpr(Pr),A : _plingo_random(E,A), _plingo_pr(E,A,Pr) }.
_plingo_densum(E,M) :- _plingo_default(E), M = #count{ A : _plingo_random(E,A), not _plingo_pr(E,A,_) }.

:~ _plingo_pr(E,Pr), _plingo_no_int(E).       [   -@log(Pr,_plingo_factor),E]
:- _plingo_pr(E,Pr), _plingo_no_int(E),           Pr = 0.

% Weight calculation for default probabilities:
% We calculate (1-Y)/M, with Y the total assigned probability
% and M the number of default outcomes
% This corresponds to log(1-Y)-log(M) (with negative weights because of optimization)

:~ _plingo_numsum(E,Y), @intpr(1)-Y > 0.   [-@log(@frac(@intpr(1)-Y,@intpr(1)),_plingo_factor),num,E]
:- _plingo_numsum(E,Y),                    @intpr(1) - Y <= 0.

:~ _plingo_densum(E,M), M > 1.             [@log(M,_plingo_factor),den,E]
:- _plingo_densum(E,M),                    M = 0.

#script (python)
from clingo import Number, String
from math import log as mathlog

def log(a, factor):
    factor = factor.number
    if str(a.type) == 'SymbolType.String':
        a =  float(eval(a.string))
    elif str(a.type) == 'SymbolType.Number':
        a = a.number
    ln = mathlog(a)
    return Number(int(ln * (10**factor)))

def frac(n,d):
    return String(f'{n.number}/{d.number}')

def intpr(a):
    factor = 10**6
    if str(a.type) == 'SymbolType.String':
        return Number(int(float(eval(a.string))*factor))
    elif str(a.type) == 'SymbolType.Number':
        return Number(a.number*factor)
#end.
'''
