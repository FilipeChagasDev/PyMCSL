"""
By Filipe Chagas
June-2022
"""

from typing import *
from random import choices

StateType = Union[int, float, str]
WeightType = Union[int, float]

def list_first_or_default(l: List, f: Callable[[Any], bool], default: Any = None) -> Any:
    for x in l:
        if f(x):
            return x
    return default

class ConstProbMarkovChain():
    def __init__(self, states: List[StateType], transitions: List[Tuple[StateType, StateType, WeightType]], initial_state: object) -> None:
        #TODO assertions
        self._states = states
        self._transitions = transitions        
        self._transition_weights = {state1: [list_first_or_default(transitions, lambda s: s[0]==state1 and s[1]==state2, (None,None,0))[2] for state2 in states] for state1 in states}
        self._state = initial_state
    
    @property
    def state(self):
        return self._state

    def foward(self):
        self._state = choices(self._states, self._transition_weights[self._state])[0]
        return self._state

class VariantProbMarkovChain():
    def __init__(self, states: List[StateType], transitions: List[Tuple[StateType, StateType, Callable[[Any],WeightType]]], initial_state: object) -> None:
        #TODO assertions
        self._states = states
        self._transitions = transitions        
        self._transition_weight_functions = {state1: [list_first_or_default(transitions, lambda s: s[0]==state1 and s[1]==state2, lambda x: 0) for state2 in states] for state1 in states}
        self._state = initial_state
    
    @property
    def state(self):
        return self._state

    def foward(self, input: Any):
        self._state = choices(self._states, [f(input) for f in self._transition_weight_functions[self._state]])[0]
        return self._state