"""
By Filipe Chagas
June-2022
"""

from typing import *
from random import choices

StateType = Union[int, float, str]
WeightType = Union[int, float]

def _first_or_default(l: List, f: Callable[[Any], bool], default: Any = None) -> Any:
    for x in l:
        if f(x):
            return x
    return default

class SimpleMarkovChain():
    """Markov Chains are graphs that represent stochastic processes based on random state transitions.
    The SimpleMarkovChain class is a Markov Chain simulator with constant transition probabilities.
    """

    def __init__(self, states: Set[StateType], transitions: List[Tuple[StateType, StateType, WeightType]], initial_state: StateType) -> None:
        """
        :param states: Set of states.
        :type states: Set[StateType], where StateType=Union[str, int, float]
        :param transitions: List of transitions. Each transition is a tuple in the format (state1, state2, weight), where state1 is the initial state, state2 is the final state and weight is a value proportional to the transition probability.
        :type transitions: List[Tuple[StateType, StateType, WeightType]]
        :param initial_state: Initial state.
        :type initial_state: StateType
        """
        assert isinstance(states, set), f'\'states\' must be a set. Given {type(states)}.'
        lstates = list(states)
        assert isinstance(transitions, list), f'\'transitions\' must be a list. Given {type(transitions)}.'
        assert all([isinstance(state, (str, int, float)) for state in states]), f'All states must be string, integer or float.'
        assert all([type(lstates[i])==type(lstates[i-1]) for i in range(1, len(lstates))]), f'All states must have the same type.'
        assert all(isinstance(transition, tuple) for transition in transitions), '\'transitions\' must be a list of tuples.'
        assert all(len(t)==3 for t in transitions), 'All the tuples of \'transitions\' must have length=3.'
        assert all([isinstance(x1, (int, float, str)) and isinstance(x2, (int, float, str)) and isinstance(x3, (int, float)) for x1,x2,x3 in transitions]), 'All the tuples of \'transitions\' must be Tuple[StateType, StateType, WeightType], where StateType=Union[int,float,str] and WeightType=Union[int, float].'
        assert all([s1 in states and s2 in states for s1, s2, w in transitions]), 'state1 and state2 in transitions tuples (state1, state2, weight) must belong to states.'
        assert initial_state in states, f'initial_state must belong to states. Given {initial_state}.'
        
        self._states = lstates
        self._transitions = transitions        
        self._transition_weights = {state1: [_first_or_default(transitions, lambda s: s[0]==state1 and s[1]==state2, (None,None,0))[2] for state2 in lstates] for state1 in lstates}
        self._state = initial_state
    
    @property
    def state(self) -> StateType:
        """Returns the current state.

        :return: Current state.
        :rtype: StateType
        """
        return self._state

    def foward(self) -> StateType:
        """Do a random transition.

        :return: State after transition.
        :rtype: StateType
        """
        self._state = choices(self._states, self._transition_weights[self._state])[0]
        return self._state