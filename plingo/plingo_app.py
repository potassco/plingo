from os.path import join
import sys
from tempfile import mkdtemp
from typing import cast, Sequence, List, Tuple, Optional

from clingo.application import Application, ApplicationOptions, Flag
from clingo.ast import AST, ProgramBuilder, parse_files, parse_string
from clingo.configuration import Configuration
from clingo.control import Control
from clingo.script import enable_python
from clingo.symbol import Function, Symbol

from .meta_problog import create_reified_problog
from .transformer import PlingoTransformer
from .query import collect_query, check_model_for_query
from .opt import MinObs, OptEnum
from .plog import get_meta_encoding
from .probability import ProbabilityModule

THEORY = """
#theory plingo{
    constant { };
    &query/1: constant, head
}.
"""


def parse_callback(ast):
    return ast


class PlingoApp(Application):
    '''
    Application extending clingo with weighted rules
    and probability calculation module.
    Plingo can compute other probabilistic logic languages
    LP^MLN, ProbLog and P-Log.
    '''
    display_all_probs: Flag
    use_unsat_approach: Flag
    two_solve_calls: Flag
    opt_enum: Flag
    use_backend: Flag
    frontend: str
    query: List[Tuple[Symbol, List[int]]]
    evidence_file: str
    balanced_models: Optional[int]
    power_of_ten: int
    temp: str
    problog: str

    program_name: str = "plingo"
    version: str = "1.1.0"

    def __init__(self):
        self.display_all_probs = Flag(False)
        self.use_unsat_approach = Flag(False)
        self.two_solve_calls = Flag(False)
        self.opt_enum = Flag(False)
        self.use_backend = Flag(False)
        self.frontend = 'plingo'
        self.query = []
        self.evidence_file = ''
        self.balanced_models = None
        self.power_of_ten = 5
        self.temp = join(mkdtemp(), 'temp.lp')
        self.problog = ''

    def _parse_frontend(self, value: str) -> bool:
        """
        Parse the given frontend mode.
        Possible options are:
        lpmln, lpmln-alt, problog and plog.
        By default the variable is set to plingo.
        """
        if value not in ['lpmln', 'lpmln-alt', 'problog', 'plog']:
            return False
        self.frontend = value
        return True

    def _parse_query(self, value: str) -> bool:
        """
        Parse query atom specified through command-line.
        This will be added to the programs as a theory atom
        '&query(value).' later, where value is the value string
        specified through the command-line.
        """
        # TODO: Keep old way as well?
        try:
            parse_string(f'&query({value}).', parse_callback)
            self.query.append(value)
        except RuntimeError:
            print(f'Query \'{value}\' cannot be parsed.')
            return False
        return True

    def _parse_evidence(self, value: str) -> bool:
        """
        Parse evidence.
        Has to be specified as (clingo) file path.
        """
        self.evidence_file = self._read(value)
        return True

    def _parse_balanced_query(self, value) -> bool:
        """
        Sets number of models N to find for
        balanced query approximation.
        This will determine max. N models
        with and without the query.
        """
        try:
            self.balanced_models = int(value)
            if self.balanced_models < 1:
                raise ValueError
            return True
        except ValueError:
            print(
                "Warning: --balanced N has to be set to an integer large than 0."
            )
            return False

    def _parse_problog(self, value) -> bool:
        with open(self.temp, 'w') as temp:
            temp.write('#show query/1.\n')
        self.problog = value
        return True

    def register_options(self, options: ApplicationOptions) -> None:
        """
        Register application option.
        """
        group = 'Plingo Options'
        options.add_flag(group, 'all,a', 'Display all probabilities',
                         self.display_all_probs)
        options.add_flag(group, 'unsat', 'Convert using unsat atoms',
                         self.use_unsat_approach)
        options.add_flag(
            group, 'two-solve-calls',
            '''Use two solve calls (first determines LPMLN stable models, second their probabilities).
                            Works only with --hr options.''',
            self.two_solve_calls)
        options.add(group, 'frontend',
                    'Frontend mode (lpmln, lpmln-alt, problog, plog).',
                    self._parse_frontend)
        options.add(group,
                    'query',
                    'Probability of query atom',
                    self._parse_query,
                    multi=True)
        options.add(group, 'evid', 'Provide evidence file',
                    self._parse_evidence)
        options.add_flag(
            group, 'opt-enum', '''Enumerates models by optimality.
                            This can be used for approximating probabilities and queries.
                            Recommended to use -q1 to suppress printing of intermediate models.''',
            self.opt_enum)
        options.add(
            group, 'balanced,b', '''Approximate query in a balanced way.
                            Use as --balanced N, where max. 2N models are determined
                            (N models with query true and false respectively).
                            This overwrites the --models option
                            This works only for a single (ground) query atom!''',
            self._parse_balanced_query)
        options.add_flag(
            group, 'use-backend',
            'Adds constraints for query approximation in backend instead of using assumptions.',
            self.use_backend)
        options.add(
            group, 'problog',
            '''Translate input to ProbLog program and save in a file.
                            Use as --problog=output.lp''', self._parse_problog)

    def validate_options(self) -> bool:
        if self.two_solve_calls and self.frontend != 'lpmln':
            print(
                'The two-solve-calls mode only works if hard rules are translated (--frontend lpmln).'
            )
            return False
        if self.balanced_models is not None and not self.opt_enum:
            print(
                'Balanced approximation only works with optimal enumeration algorithm (--opt-enum)'
            )
            return False
        if self.use_backend and self.balanced_models is not None:
            print(
                'The --use-backend option only works with balanced query approximation (--balanced N).'
            )
            return False
        return True

    def _read(self, path: str):
        if path == "-":
            return sys.stdin.read()
        with open(path) as file_:
            return file_.read()

    def _save_translation(self, rule):
        rule = str(rule)
        if rule != '#program base.':
            with open(self.temp, 'a') as lp:
                lp.write(f'{rule}\n')

    def _convert(self, ctl: Control, files: Sequence[str]):
        options = [
            self.frontend, self.use_unsat_approach, self.two_solve_calls,
            self.power_of_ten
        ]
        pt = PlingoTransformer(options)
        if self.problog:
            parse_files(
                files, lambda stm: self._save_translation(
                    pt.visit(stm, file=self.temp)))
        else:
            with ProgramBuilder(ctl) as b:
                parse_files(
                    files,
                    lambda stm: b.add(cast(AST, pt.visit(stm, builder=b))))

    def _preprocessing(self, ctl: Control,
                       files: Sequence[str]) -> Tuple[Configuration, MinObs]:
        '''
        Performs some preprocessing.
        '''
        ctl.add("base", [], THEORY)
        ctl.add("base", [], self.evidence_file)

        # Add meta file for calculating P-Log
        if self.frontend == 'plog':
            enable_python()
            ctl.add("base", [], get_meta_encoding())
            ctl.add("base", [], f'#const _plingo_factor={self.power_of_ten}.')
            if self.problog:
                with open(self.temp, 'a') as lp:
                    lp.write(f'{get_meta_encoding()}\n')
                    lp.write(f'#const _plingo_factor={self.power_of_ten}.\n')
        if self.two_solve_calls:
            ctl.add("base", [], '#external _plingo_ext_helper.')
        # TODO: Make sure the _ext_helper atom is not contained in the program.
        # TODO: Change number of underscores for _ext_helper and plog meta atoms

        if not files:
            files = ["-"]
        self._convert(ctl, files)

        # Add queries specified through command-line to program as theory
        if self.query != []:
            for q in self.query:
                ctl.add("base", [], f'&query({q}).')
            self.query = []

        obs = MinObs(self.opt_enum.flag)
        ctl.register_observer(obs)
        return obs

    def _solve(self, ctl: Control, obs: MinObs):
        '''
        Solves either for most probable stable model, all models
        or enumerates models by optimality.
        The latter option can be used for approximate calculations.
        '''
        if self.opt_enum.flag:
            ctl.configuration.solve.opt_mode = 'optN'
            opt = OptEnum(self.query, self.balanced_models, self.use_backend)
            model_costs, self.query = opt.optimize(ctl, obs)
        else:
            bound_hr = 2**63 - 1
            if self.two_solve_calls:
                # First solve call
                # Soft rules are deactivated
                # TODO: Suppress output of first solve call, add flag
                # TODO: Activate this per flag

                ctl.assign_external(Function("_plingo_ext_helper"), False)
                with ctl.solve(yield_=True) as h:
                    for m in h:
                        bound_hr = m.cost[0]
                # TODO: Don't show _ext_helper
                ctl.assign_external(Function("_plingo_ext_helper"), True)

            if self.display_all_probs or self.query != []:
                ctl.configuration.solve.opt_mode = f'enum, {bound_hr}, {(2**63)-1}'
                ctl.configuration.solve.models = 0

            model_costs = []
            with ctl.solve(yield_=True) as handle:
                for model in handle:
                    if self.display_all_probs or self.query != []:
                        model_costs.append(model.cost)
                        if self.query != []:
                            self.query = check_model_for_query(
                                self.query, model)
        return model_costs

    def _probabilities(self, model_costs: List[int], priorities: List[int]):
        '''
        Calls probability module and prints probababilities.
        '''
        if 0 not in priorities:
            # TODO: Should this be error or warning?
            print('No soft weights in program. Cannot calculate probabilites')
            return
        # TODO: What about case where there are other priorities than 0/1?
        # elif not self.two_solve_calls and any(
        #         x > 1 for x in priorities):
        #     print(priorities)
        probs = ProbabilityModule(
            model_costs, priorities,
            [self.frontend, self.two_solve_calls, self.power_of_ten])
        if self.display_all_probs:
            probs.print_probs()
        if self.query != []:
            probs.get_query_probability(self.query)

    def main(self, ctl: Control, files: Sequence[str]):
        '''
        Parse clingo program with weights and convert to ASP with weak constraints.
        '''
        obs = self._preprocessing(ctl, files)
        if self.problog:
            create_reified_problog(self.temp, self.problog)
        else:
            ctl.ground([("base", [])])
            self.query = collect_query(ctl.theory_atoms, self.balanced_models)
            model_costs = self._solve(ctl, obs)

            if model_costs != []:
                self._probabilities(model_costs, obs.priorities)
