"""
By Filipe Chagas
June-2022
"""

from typing import *
import numpy as np
from pandas import DataFrame

class ContextType():
    def __init__(self) -> None:
        pass

def raise_read_only_exception(p1,p2,p3):
    raise Exception('Attributes of a past context are all read-only')

class SubSimulationEnv:
    """
    The SubSimulationEnv class provides a basic framework for a multi-step 
    simulation. The subsimulation has a set of variables, each with a name, 
    a data type, and a default value. In each step of the simulation, a 
    callback function is called receiving the current step number and a
    ContextType object with all the variables, being able to change the
    current states of the variables through this object. At the end of each
    simulation step, the current states of the variables are recorded in a 
    table with the history of values of all variables.
    """

    def __init__(self, variables: List[Tuple[str, type, object]], prepare_function: Callable[[ContextType], None], run_step_function: Callable[[ContextType, int], None]) -> None:
        """
        Args:
            variables (List[Tuple[str, type, object]]): list of simulation variables in the format [(variable_name, variable_type, default_value)].
            prepare_function (Callable[[ContextType], None]): function to prepare the simulation context.
            run_step_function (Callable[[ContextType, int], None]): function to run the simulation steps.
        """
        assert isinstance(variables, list), f'Argument of \'variables\' must be a list, but a {type(variables)} object was received.'
        assert all([isinstance(var_name, str) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_type, type) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_default, var_type) for var_name, var_type, var_default in variables]), f'Some default value in \'variables\' list does not correspond to its variable\'s type.'
        assert all([var_name not in ('past', 'getstate', 'setstate') for var_name, var_type, var_default in variables]), 'Names \'past\', \'getstate\' and \'setstate\' are internally reserved and forbidden for variables.'
        assert isinstance(prepare_function, Callable), f'Argument of \'prepare_function\' must be a Callable, but a {type(prepare_function)} object was received.'
        assert isinstance(run_step_function, Callable), f'Argument of \'run_step_function\' must be a Callable, but a {type(run_step_function)} object was received.'

        self._variables = variables
        self._prepare_function = prepare_function
        self._run_step_function = run_step_function
        self._steps_taken = 0
        
        #build a dictionary for mapping variable's types
        self._var_types = {var_name:var_type for var_name, var_type, var_default in variables}

        #Creates an empty historic table for the variables
        self._history = {var_name:[] for var_name, var_type, var_default in variables}
        
        #Creates a dictionary for states
        self._var_states = {var_name:var_default for var_name, var_type, var_default in variables}
        
    def _log_states(self):
        """Internal method. 
        Push current states in _var_states to the historic table _history.
        """
        for var_name, var_type, var_default in self._variables:
            var_state = self._var_states[var_name]
            assert isinstance(var_state, var_type) or isinstance(var_state, type(None))
            self._history[var_name].append(self._var_states[var_name])

    def _get_context_obj(self) -> ContextType:
        """Internal method.
        Build dinamically a ContexType subclass that provides access to states in _var_states
        and returns a instance of it.

        Returns:
            ContextType: New ContexType object.
        """
        def _get_past_method(contextobj: ContextType):
            """The 'past' method gives a read-only context with all states of 'n' steps back.
            """
            def past(n):
                assert isinstance(n, int), f'The value of the \'n\' parameter in the \'past\' method must be integer, but type(n)={type(n)}.'
                assert n >= 1, f'The value of the \'n\' parameter in the \'past\' method must be n>=1, but n={n}.'
                assert n < self._steps_taken, f'The value of the \'n\' parameter in the \'past\' method must be less than the number of steps taken ({self._steps_taken}), but n={n}.'
                
                past_context_content = {var_name:self._history[var_name][-n] for var_name in self._history.keys()}
                past_context_content['__setattr__'] = raise_read_only_exception
                
                MyReadOnlyContextType = type(f'ReadOnlyContext{id(contextobj)}', (ContextType,), past_context_content)

                return MyReadOnlyContextType()
            return past

        def _get_getstate_method(contextobj: ContextType):
            """The 'getstate' method returns the state of a variable.
            """
            def getstate(var_name):
                assert isinstance(var_name, str), f'var_name must be a string. Given {var_name} of type {type(var_name)}.'
                assert var_name in self._var_states.keys(), f'variable {var_name} does not exists.'
                return self._var_states[var_name]
            return getstate
        
        def _get_setstate_method(contextobj: ContextType):
            """The 'setstate' method sets a value to a variable.
            """
            def setstate(var_name, var_value):
                assert isinstance(var_name, str), f'var_name must be a string. Given {var_name} of type {type(var_name)}.'
                assert var_name in self._var_states.keys(), f'variable {var_name} does not exists.'
                assert isinstance(var_value, self._var_types[var_name]), f'not allowed assignment of value {var_value} of type {type(var_value)} to variable {var_name} of type {self._var_types[var_name]}.'
                assert var_name != 'past', f'past is a method, not a variable.'
                self._var_states[var_name] = var_value
            return setstate

        def _set_attribute(contextobj, var_name, var_value):
            assert var_name in self._var_states.keys(), f'variable {var_name} does not exists.'
            assert isinstance(var_value, self._var_types[var_name]), f'not allowed assignment of value {var_value} of type {type(var_value)} to variable {var_name} of type {self._var_types[var_name]}.'
            assert var_name != 'past', f'past is a method, not a variable.'
            self._var_states[var_name] = var_value
        
        def _get_attribute(contextobj, var_name):
            if var_name == 'past': #call to the past method
                return _get_past_method(contextobj)
            elif var_name == 'getstate': #call to the getstate method
                return _get_getstate_method(contextobj)
            elif var_name == 'setstate': #call to the setstate method
                return _get_setstate_method(contextobj)
            else:
                assert var_name in self._var_states.keys(), f'variable {var_name} does not exists.'
                return self._var_states[var_name]

        MyContextType = type(f'Context{id(self)}', (ContextType,), {
            '__setattr__': _set_attribute,
            '__getattribute__': _get_attribute
        })

        return MyContextType()

    def _prepare(self):
        """Internal method.
        Calls the simulation preparing callback.
        """
        context = self._get_context_obj()
        self._prepare_function(context)

    def _run_step(self, step: int):
        """Internal method.
        Calls the simulation run-step callback.
        Args:
            step (int): step number.
        """
        context = self._get_context_obj()
        self._run_step_function(context, step)

    def run_steps(self, n: int):
        """Run 'n' steps of the simulation.

        Args:
            n (int): number of steps.
        """
        assert isinstance(n, int)
        assert n > 0

        self._prepare()
        for step in range(n):
            self._run_step(step)
            self._log_states()
            self._steps_taken += 1

    def get_history_dataframe(self) -> DataFrame:
        """Get variables history as a Pandas Dataframe. 

        Returns:
            DataFrame: variables history dataframe.
        """
        return DataFrame(self._history)

    def get_numpy_history(self) -> Dict[str, np.ndarray]:
        """Get variables history as a dictionary of NumPy arrays.

        Returns:
            Dict[str, np.ndarray]: variables history.
        """
        return {var_name:np.array(self._history[var_name]) for var_name in self._history.keys()}