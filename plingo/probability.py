from math import exp
from typing import List, Union, Tuple, Dict

from clingo.application import Flag
from clingo.symbol import Symbol
from numpy import intersect1d


class ProbabilityModule():
    '''
    Calculates probabilities of models and query atoms.
    '''
    mode: str
    two_solve_calls: Flag
    power_of_ten: int
    priorities: List[int]
    model_weights: List[float]
    stable_models: List[int]
    model_probs: List[float]

    def __init__(self, model_costs: List[int], priorities: List[int],
                 options: Union[str, Flag, int]):
        # TODO: Do weights need to be saved?
        self.frontend = options[0]
        self.two_solve_calls = options[1].flag
        self.power_of_ten = options[2]
        self.priorities = priorities
        self.model_weights = []
        self.stable_models = []
        self.model_probs = []
        self.calculate_probabilites(model_costs)

    def calculate_probabilites(self, model_costs: List[int]):
        '''
        Calculates probabilities based on list of model costs.
        If hard rules have been translated
        find only stable models of LP^MLN
        (ones with max hard rules satisfied).
        '''
        # Extract only level 0 costs which correspond to weights and apply calculations
        self.model_weights = [costs[-1] for costs in model_costs]
        self.model_weights = [
            exp(-(w * 10**(-self.power_of_ten))) for w in self.model_weights
        ]
        if self.frontend == 'lpmln' and self.priorities != [0]:
            hard_weights = [costs[0] for costs in model_costs]
            min_alpha = min(hard_weights)
            self.model_weights = [
                w if hard_weights[i] == min_alpha else 0
                for i, w in enumerate(self.model_weights)
            ]

        self.stable_models = [
            i for i, w in enumerate(self.model_weights) if w != 0
        ]
        normalization_const = sum(self.model_weights)
        self.model_probs = [
            w / normalization_const for w in self.model_weights
        ]
        # TODO: Unittest/Check that probabilities sum up to 1

    def print_probs(self):
        '''
        Prints probabilities of stable models.
        '''
        print('\n')
        for s in self.stable_models:
            current_prob = self.model_probs[s]
            # TODO: Filter very small probs or not?
            # if current_prob < 0.000001:
            #     continue
            print(f'Probability of Answer {s+1}: {current_prob:.5f}')
            # print(f'Probability of Answer {s+1}: {current_prob}')
        # TODO: Round off probabilities?
        print('\n')

    def get_query_probability(self, queries: List[Tuple[Symbol, List[int]]],
                              atoms_to_check: Dict):
        '''
        Prints probabilities of query atoms.
        '''
        print('\n')
        for q in queries:
            query = str(q[0])
            condition = str(q[1])
            if condition == "":
                prob = sum([
                    self.model_probs[idx]
                    for idx in atoms_to_check[query]['models']
                ])
                print(f'{query}: {prob:.5f}')
            else:
                # P(A | B) = P(A & B) / P(B),
                # where A is query and B is condition
                intersection = list(
                    set(atoms_to_check[query]['models'])
                    & set(atoms_to_check[condition]['models']))
                prob_union = sum(
                    [self.model_probs[idx] for idx in intersection])
                prob_condition = sum([
                    self.model_probs[idx]
                    for idx in atoms_to_check[condition]['models']
                ])
                prob = prob_union / prob_condition
                print(f'{query} | {condition}: {prob:.5f}')
        print('\n')
