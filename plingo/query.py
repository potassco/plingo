from typing import Tuple, List, Optional, Dict

from clingo.solving import Model
from clingo.symbol import Function, Number, String, Symbol
from clingo.theory_atoms import TheoryAtom


def _convert_theory_arg(arg: Symbol) -> Symbol:
    '''
    Converts the argument of a theory
    &query/1 atom to the correct Symbol.
    '''
    theory_type = str(arg.type).replace('TheoryTermType.', '')
    if theory_type == 'Symbol':
        if arg.name.startswith('"'):
            return String(str(arg.name).strip('"'))
        else:
            return Function(arg.name)
    elif theory_type == 'Number':
        return Number(arg.number)
    elif theory_type == 'Function':
        args = [_convert_theory_arg(targ) for targ in arg.arguments]
        return Function(arg.name, args)
    elif theory_type == 'Tuple':
        args = [_convert_theory_arg(targ) for targ in arg.arguments]
        return Function("", args)


def _convert_theory_query(atom: TheoryAtom) -> Function:
    '''
    Converts a &query/1 atom to a Symbol.
    '''
    # query_atom = theory_atom.term.arguments[0]
    name = atom.name
    args = []
    if atom.arguments != []:
        args = [_convert_theory_arg(arg) for arg in atom.arguments]
    return Function(name, args)


def collect_query(theory_atoms: List[TheoryAtom],
                  balanced_models: Optional[int]):
    '''
    Collect all queries from theory atoms.
    For balanced query mode only one query atom is allowed.
    '''
    queries = []
    atoms_to_check = {}
    for t in theory_atoms:
        if t.term.name == 'query':
            query = _convert_theory_query(t.term.arguments[0])
            atoms_to_check[str(query)] = {'symbol': query, 'models': []}
            condition = ""
            if len(t.term.arguments) > 1:
                condition = _convert_theory_query(t.term.arguments[1])
                atoms_to_check[str(condition)] = {
                    'symbol': condition,
                    'models': []
                }
            queries.append((query, condition))
    if balanced_models is not None and len(queries) > 1:
        raise RuntimeError(
            'Only one (ground) query atom can be specified for balanced approximation.'
        )
    return queries, atoms_to_check


def check_model_for_query(queries: Dict,
                          model: Model,
                          model_number: Optional[int] = None):
    '''
    Efficiently checks if a model contains a query
    and if so, saves the current model number.
    '''
    if model_number is None:
        model_number = model.number - 1
    for qa in queries.values():
        if model.contains(qa['symbol']):
            qa['models'].append(model_number)
    return queries
