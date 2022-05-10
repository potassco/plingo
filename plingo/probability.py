from typing import List, Union, Tuple

from clingo.application import Flag
from clingo.symbol import Symbol

import numpy as np
# from numpy.typing import ndarray


class ProbabilityModule():
    '''
    Calculates probabilities of models and query atoms.
    '''
    translate_hr: Flag
    two_solve_calls: Flag
    power_of_ten: int
    priorities: List[int]
    model_weights: np.ndarray
    stable_models: np.ndarray
    model_probs: np.ndarray

    def __init__(self, model_costs: List[int], priorities: List[int],
                 options: Union[Flag, Flag, int]):
        # TODO: Do weights need to be saved?
        self.translate_hr = options[0].flag
        self.two_solve_calls = options[1].flag
        self.power_of_ten = options[2]
        self.priorities = priorities
        self.model_weights = []
        self.stable_models = []
        self.model_probs = []
        self.calculate_probabilites(np.array(model_costs))

    def calculate_probabilites(self, model_costs: np.ndarray):
        '''
        Calculates probabilities based on list of model costs.
        If hard rules have been translated
        find only stable models of LP^MLN
        (ones with max hard rules satisfied).
        '''
        self.model_weights = np.exp(-(model_costs * 10**(-self.power_of_ten)))
        if self.two_solve_calls:
            self.model_weights = self.model_weights[:, -1]
        elif self.translate_hr and self.priorities != [0]:
            hard_weights = model_costs[:, 0]
            min_alpha = hard_weights.min()
            self.model_weights = self.model_weights[:, -1]
            self.model_weights[hard_weights != min_alpha] = 0

        self.model_weights = self.model_weights.flatten()
        self.stable_models = np.where(self.model_weights != 0)[0]
        normalization_const = self.model_weights.sum()
        self.model_probs = self.model_weights / normalization_const
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

    def get_query_probability(self, queries: List[Tuple[Symbol, List[int]]]):
        '''
        Prints probabilities of query atoms.
        '''
        print('\n')
        for q in queries:
            prob = self.model_probs[q[1]].sum()
            print(f'{str(q[0])}: {prob:.5f}')
        print('\n')
