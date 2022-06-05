"""
By Filipe Chagas
June-2022
"""

from typing import *
from capsule import Capsule
import pandas as pd

class SubSimulationEnv:
    def __init__(self, variables: List[Tuple[str, type]], prepare_function: Callable[[Capsule], None], run_step_function: Callable[[Capsule, int], None]) -> None:
        assert(isinstance(variables, list))
        assert(all([isinstance(var_name, str) for var_name, var_type in variables]))
        assert(all([isinstance(var_type, type) for var_name, var_type in variables]))
        assert(isinstance(prepare_function, Callable))
        assert(isinstance(run_step_function, Callable))

        self._variables = variables
        self._prepare_function = prepare_function
        self._run_step_function = run_step_function
        self._steps_taken = 0
        
        #build a dictionary for mapping variable's types
        self._var_types = {var_name:var_type for var_name, var_type in variables}

        #Creates an empty historic table for the variables
        self._history = {var_name:[] for var_name, var_type in variables}
        
        #Creates a dictionary for states
        self._var_states = {var_name:None for var_name, var_type in variables}
        
    def _log_states(self):
        for var_name, var_type in self._variables:
            var_state = self._var_states[var_name]
            assert(isinstance(var_state, var_type) or isinstance(var_state, type(None)))
            self._history[var_name].append(self._var_states[var_name])

    def get_capsule(self):
        capsule = Capsule(self._variables)
        for var_name, var_type in self._variables:
            capsule.set_variable(var_name, self._var_states[var_name])
        return capsule

    def set_capsule(self, capsule: Capsule):
        assert(isinstance(capsule, Capsule))

        for var_name, var_type in self._variables:
            self._var_states[var_name] = capsule.get_variable(var_name)

    def _prepare(self):
        self._prepare_function(self.get_capsule())

    def _run_step(self, step: int):
        self._run_step_function(self.get_capsule(), step)

    def _run_steps(self, n: int):
        assert(isinstance(n, int))
        assert(n > 0)

        self._prepare()
        for step in range(n):
            self._run_step(step)
            self._log_states()
            self._steps_taken += 1

    def get_dataframe(self):
        return pd.DataFrame(self._history)