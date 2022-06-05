"""
By Filipe Chagas
June-2022
"""

from typing import *

class Capsule:
    def __init__(self, variables: List[Tuple[str, type]], history: Dict[str, List], steps_taken: int) -> None:
        assert(isinstance(variables, list))
        assert(all([isinstance(var_name, str) for var_name, var_type in variables]))
        assert(all([isinstance(var_type, type) for var_name, var_type in variables]))
        assert(isinstance(history, dict))
        assert(all([isinstance(var_name, str) for var_name in history.keys()]))
        assert(isinstance(steps_taken, int))

        self._variables = variables
        self._history = history
        self._steps_taken = steps_taken

        #build a dictionary for mapping variable's types
        self._var_types = {var_name:var_type for var_name, var_type in variables}

        #Creates an attribute for each variable
        for var_name, var_type in variables:
            self.__dict__[var_name] = None

    def set_variable(self, var_name: str, value: object):
        assert(var_name in self._var_types.keys())
        assert(isinstance(value, self._var_types[var_name]))
        self.__dict__[var_name] = value

    def get_variable(self, var_name: str,):
        assert(var_name in self._var_types.keys())
        value = self.__dict__[var_name]
        assert(isinstance(value, self._var_types[var_name]))
        return value

    def back(self, n: int):
        assert(isinstance(n, int))
        assert(n > 0)
        assert(n < self._steps_taken)

        past_history = self._history.copy()
        for i in range(n):
            past_states = {var_name:past_history[var_name].pop() for var_name in past_history.keys()}

        capsule = Capsule(self._variables, past_history, self._steps_taken-n)

        for var_name in past_states.keys():
            capsule.set_variable(var_name, past_states[var_name])

        return capsule