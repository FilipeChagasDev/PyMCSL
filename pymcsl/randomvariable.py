"""
By Filipe Chagas
June-2022
"""

from typing import *
from random import choices

class DiscreteRandomVariable():
    """Random variables are variables that give unpredictable results. 
    Discrete random variables have an alphabet, which is a set of possible outcomes, and a outcoming probability associated with each value in the alphabet. The act of getting a outcome from a random variable is called 'evaluation'.
    """
    def __init__(self, alphabet_and_weights: Dict[Union[str, int, float], Union[int, float]]):
        """
        :param alphabet_and_weights: Dictionary whose set of keys is the alphabet and the items are the probabilities. Format {outcome, probability}. 
        :type alphabet_and_weights: Dict[Union[str, int, float], Union[int, float]]
        """
        self._alphabet = [x for x in alphabet_and_weights.keys()]
        self._weights = [alphabet_and_weights[x] for x in alphabet_and_weights.keys()]

    def evaluate(self) -> Union[str, int, float]:
        """Get an outcome.

        :return: outcome.
        :rtype: Union[str, int, float]
        """
        return choices(self._alphabet, self._weights)[0]