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
