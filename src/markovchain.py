"""
By Filipe Chagas
June-2022
"""

from typing import *
from random import choices

StateType = Union[int, float, str]
WeightType = Union[int, float]

def first_or_default(l: List, f: Callable[[Any], bool], default: Any = None) -> Any:
    for x in l:
        if f(x):
            return x
    return default

class SimpleMarkovChain():
    """
    Simple Markov Chain simulator.
    """

    def __init__(self, states: List[StateType], transitions: List[Tuple[StateType, StateType, WeightType]], initial_state: StateType) -> None:
        """
        Args:
            states (List[StateType]): List of states (StateType=Union[str, int, float]).
            transitions (List[Tuple[StateType, StateType, WeightType]]): List of transitions. Each transition is a tuple in the format (state1, state2, weight), where state1 is the initial state, state2 is the final state and weight is a value proportional to the transition probability.
            initial_state (StateType): Initial state.
        """
        assert isinstance(states, list), f'\'states\' must be a list. Given {type(states)}.'
        assert isinstance(transitions, list), f'\'transitions\' must be a list. Given {type(transitions)}.'
        assert all([isinstance(state, (str, int, float)) for state in states]), f'All states must be string, integer or float.'
        assert all([type(states[i])==type(states[i-1]) for i in range(1, len(states))]), f'All states must have the same type.'
        assert all(isinstance(transition, tuple) for transition in transitions), '\'transitions\' must be a list of tuples.'
        assert all(len(t)==3 for t in transitions), 'All the tuples of \'transitions\' must have length=3.'
        assert all([isinstance(x1, (int, float, str)) and isinstance(x2, (int, float, str)) and isinstance(x3, (int, float)) for x1,x2,x3 in transitions]), 'All the tuples of \'transitions\' must be Tuple[StateType, StateType, WeightType], where StateType=Union[int,float,str] and WeightType=Union[int, float].'
        assert all([s1 in states and s2 in states for s1, s2, w in transitions]), 'state1 and state2 in transitions tuples (state1, state2, weight) must belong to states.'
        assert initial_state in states, f'initial_state must belong to states. Given {initial_state}.'
        
        self._states = states
        self._transitions = transitions        
        self._transition_weights = {state1: [first_or_default(transitions, lambda s: s[0]==state1 and s[1]==state2, (None,None,0))[2] for state2 in states] for state1 in states}
        self._state = initial_state
    
    @property
    def state(self) -> StateType:
        """
        Returns:
            StateType: current state.
        """
        return self._state

    def foward(self) -> StateType:
        """
        Do a transition.
        Returns:
            StateType: state after the transition.
        """
        self._state = choices(self._states, self._transition_weights[self._state])[0]
        return self._state