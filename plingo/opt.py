from typing import cast, Optional, Sequence, Tuple, Dict, List

from clingo.backend import Backend, Observer
from clingo.configuration import Configuration
from clingo.control import Control
from clingo.solving import SolveResult, Model
from clingo.statistics import StatisticsMap
from clingo.symbol import Symbol

from .query import check_model_for_query


class MinObs(Observer):
    '''
    Observer to extract ground minimize constraint.
    '''
    opt_enum: bool
    priorities: List[int]
    literals: Dict[int, List[Tuple[int, int]]]

    def __init__(self, opt_enum=False):
        self.opt_enum = opt_enum
        self.priorities = []
        if self.opt_enum:
            self.literals = {}

    def minimize(self, priority: int, literals: Sequence[Tuple[int, int]]):
        '''
        Intercept minimize constraint and add it to member `literals`.
        '''
        self.priorities.append(priority)
        if self.opt_enum:
            self.literals.setdefault(priority, []).extend(literals)


class OptEnum:
    '''
    Class implementing optimal model enumeration.
    This can be used to approximate probabilities of stable models.
    Optionally stable models can be found in a balanced way
    when calculating probabilities of a query. 
    '''
    _aux_level: Dict[Tuple[int, int], int]
    _proven: int
    _intermediate: int
    model_costs: List[int]
    query: List[Tuple[Symbol, List[int]]]
    num_balanced_models: Optional[int]
    reached_max: Optional[bool]
    assumptions: List[Tuple[Symbol, bool]]
    use_backend: bool

    def __init__(self, query, balanced=None, use_backend=False):
        self._aux_level = {}
        self._proven = 0
        self._intermediate = 0
        self.model_costs = []
        self.query = query
        self.num_balanced_models = balanced
        self.reached_max = None
        self.assumptions = []
        self.use_backend = use_backend

    def _check_reached_max(self):
        '''
        Used for balanced query mode.
        Checks whether the max. number of models 
        with (or without) the query have been found already.
        '''
        m_with_q = len(self.query[0][1])
        if m_with_q == self.num_balanced_models:
            self.reached_max = True
        m_without_q = len(self.model_costs) - m_with_q
        if m_without_q == self.num_balanced_models:
            self.reached_max = False
        # Update assumptions for next solve calls
        if self.reached_max is not None and not self.use_backend:
            self.assumptions.append((self.query[0][0], not self.reached_max))

    def _on_model(self, model: Model) -> bool:
        '''
        Intercept models.
        This function counts optimal and intermediate models.
        If the balanced, approximate query mode is activated
        it also checks whether enough models with(out) the query
        have been found and adds a corresponding clause.
        '''
        # if self._heu:
        #     self._heu.on_model(model)
        if model.optimality_proven:
            self.model_costs.append(model.cost)
            if self.query != []:
                self.query = check_model_for_query(self.query, model,
                                                   self._proven)
                if self.num_balanced_models is not None and self.reached_max is None:
                    self._check_reached_max()
                    if self.reached_max:
                        model.context.add_clause([(self.query[0][0], False)])
                    elif self.reached_max is False:
                        model.context.add_clause([(self.query[0][0], True)])
            self._proven += 1

        else:
            self._intermediate += 1
        return True

    def _add_upper_bound(self, backend: Backend, wlits: Sequence[Tuple[int,
                                                                       int]],
                         bound: int, level: Optional[int]):
        '''
        Adds the constraint `a <> { wlits } < bound` and returns literal `a`.
        If level is None, then an integrity constraint is added and no
        auxiliary literal is introduced.
        This function reuses literals introduced in earlier iterations.
        '''
        hd = []
        if level is not None:
            if (level, bound) in self._aux_level:
                return self._aux_level[(level, bound)]
            hd.append(backend.add_atom())
            self._aux_level[(level, bound)] = hd[0]

        lower = -bound
        wlits_lower = []
        for lit, w in wlits:
            if w > 0:
                lower += w
                lit = -lit
            else:
                w = -w
            wlits_lower.append((lit, w))
        backend.add_weight_rule(hd, lower, wlits_lower)
        return hd[0] if hd else None

    def _set_upper_bound(self, backend: Backend,
                         minimize: Sequence[Sequence[Tuple[int, int]]],
                         bound: Sequence[int]):
        '''
        Adds constraints discarding solutions lexicographically smaller or
        equal than the bound.
        The weighted literals in the minimize variable directly correspond to
        how the solver represents minimize constraints.
        '''
        assert minimize and len(minimize) == len(bound)
        if len(minimize) == 1:
            self._add_upper_bound(backend, minimize[0], bound[0], None)
        else:
            # Note: we could also introduce a chain. But then there are
            # typically few priorities and this should resolve nicely.
            # :- l0 <= b0-1
            # :- l0 <= b0 && l1 <= b1-1
            # :- l0 <= b0 && l1 <= b1 && l2 <= b2-1
            # ...
            # :- l0 <= b0 && l1 <= b1 && l2 <= b2 && ... && ln <= bn
            prefix = []
            for i, (wlits, value) in enumerate(zip(minimize, bound)):
                if i == len(minimize) - 1:
                    prefix.append(
                        self._add_upper_bound(backend, wlits, value, i))
                    backend.add_rule([], prefix)
                else:
                    prefix.append(
                        self._add_upper_bound(backend, wlits, value - 1, i))
                    backend.add_rule([], prefix)
                    prefix[-1] = self._add_upper_bound(backend, wlits, value,
                                                       i)

    def _on_statistics(self, step: StatisticsMap, accu: StatisticsMap):
        '''
        Sets optimization specific statistics.
        '''
        update_dict = {
            'Enumerate': {
                'Enumerated': self._proven,
                'Intermediate': self._intermediate
            }
        }
        if self.query != []:
            update_dict['Enumerate']['Contain Query'] = len(self.query[0][1])
        accu.update(update_dict)

    def optimize(self, ctl: Control, obs: MinObs):
        '''
        Run optimal solution enumeration algorithm.
        Optionally for approximating a query this
        can find models which do/do not contain
        the query in a balanced way.
        '''
        # if self._restore:
        #     self._heu = RestoreHeu()
        #     ctl.register_propagator(self._heu)

        if self.num_balanced_models is not None:
            ctl.configuration.solve.models = 2 * self.num_balanced_models
            if self.use_backend:
                query_literal = [
                    sa.literal for sa in ctl.symbolic_atoms
                    if sa.symbol == self.query[0][0]
                ][0]

        res = cast(
            SolveResult,
            ctl.solve(on_model=self._on_model,
                      on_statistics=self._on_statistics))

        solve_config = cast(Configuration, ctl.configuration.solve)

        num_models = int(cast(str, solve_config.models))

        minimize = [
            x[1] for x in sorted(obs.literals.items(), key=lambda x: -x[0])
        ]
        try:
            while (res.satisfiable and not res.interrupted and minimize
                   and 'costs' in ctl.statistics['summary']):
                summary = ctl.statistics['summary']
                if num_models > 0:
                    num_models -= int(summary['models']['optimal'])
                    if num_models <= 0:
                        break
                    solve_config.models = num_models
                costs = cast(
                    Tuple[int],
                    tuple(int(x) for x in ctl.statistics['summary']['costs']))

                with ctl.backend() as backend:
                    self._set_upper_bound(backend, minimize, costs)
                    if self.use_backend:
                        if self.reached_max:
                            backend.add_rule([], [query_literal])
                            self.use_backend = False
                        elif self.reached_max is False:
                            backend.add_rule([], [-query_literal])
                            self.use_backend = False

                # if self._heu is not None:
                #     self._heu.set_restore(costs)
                res = cast(
                    SolveResult,
                    ctl.solve(assumptions=self.assumptions,
                              on_model=self._on_model,
                              on_statistics=self._on_statistics))
        except RuntimeError:
            # This catches a timeout/keyboard interrupt and still returns the already found model costs
            pass
        return self.model_costs, self.query
