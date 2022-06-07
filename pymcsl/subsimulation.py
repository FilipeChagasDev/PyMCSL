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

def _raise_read_only_exception(p1,p2,p3):
    raise Exception('Attributes of a past context are all read-only')

class SubSimulationEnv:
    """
    The SubSimulationEnv class provides a basic framework for a multi-step simulation. The subsimulation has a set of variables, each with a name, a data type, and a default value. In each step of the simulation, a callback function is called receiving the current step number and a ContextType object with all the variables, being able to change the current states of the variables through this object. At the end of each simulation step, the current states of the variables are recorded in a table with the history of values of all variables.
    """

    def __init__(self, variables: List[Tuple[str, type, object]], begin_function: Callable[[ContextType], None], step_function: Callable[[ContextType, int], None]) -> None:
        """
        :param variables: List of simulation variables in the format [(variable_name, variable_type, default_value)].
        :type variables: List[Tuple[str, type, object]]
        :param begin_function: Function to prepare the simulation context before the first step.
        :type begin_function: Callable[[ContextType], None]
        :param step_function: Function to run the simulation steps.
        :type step_function: Callable[[ContextType, int], None]
        """
        assert isinstance(variables, list), f'Argument of \'variables\' must be a list, but a {type(variables)} object was received.'
        assert all([isinstance(var_name, str) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_type, type) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_default, var_type) for var_name, var_type, var_default in variables]), f'Some default value in \'variables\' list does not correspond to its variable\'s type.'
        assert all([var_name not in ('past', 'getstate', 'setstate') for var_name, var_type, var_default in variables]), 'Names \'past\', \'getstate\' and \'setstate\' are internally reserved and forbidden for variables.'
        assert isinstance(begin_function, Callable), f'Argument of \'begin_function\' must be a Callable, but a {type(begin_function)} object was received.'
        assert isinstance(step_function, Callable), f'Argument of \'step_function\' must be a Callable, but a {type(step_function)} object was received.'

        self._variables = variables
        self._begin_function = begin_function
        self._step_function = step_function
        self._steps_taken = 0
        
        #build a dictionary for mapping variable's types
        self._var_types = {var_name:var_type for var_name, var_type, var_default in variables}

        #Creates an empty historic table for the variables
        self._history = {var_name:[] for var_name, var_type, var_default in variables}
        
        #Creates a dictionary for states
        self._var_states = {var_name:var_default for var_name, var_type, var_default in variables}
        
        #Creates a dictionary for ancillary objects
        self._aux = dict()

    @property
    def variables_names(self) -> List[str]:
        """
        :return: List with all variables names.
        :rtype: List[str]
        """
        return [var_name for var_name, var_type, var_default in self._variables]

    @property
    def variables_types(self) -> Dict[str, type]:
        """Returns a dictionary with all variables types.

        :return: Dictionary in the format {variable_name: variable_type}.
        :rtype: Dict[str, type]
        """
        return self._var_types.copy()

    @property
    def variables_states(self) -> Dict[str, Any]:
        """Returns a dictionary with all variables states.

        :return: Dictionary in the format {variable_name: variable_state}.
        :rtype: Dict[str, Any]
        """
        return self._var_states.copy()

    @property
    def auxiliary_objects(self) -> Dict[str, Any]:
        """Returns a dictionary with all the auxiliary objects.

        :return: Dictionary in the format {attribute_name: object}.
        :rtype: Dict[str, Any]
        """
        return self._aux.copy()

    def get_variable_type(self, var_name: str) -> type:
        """Returns the type of a specific variable.

        :param var_name: Variable name.
        :type var_name: str
        :return: Variable type.
        :rtype: type
        """
        assert isinstance(var_name, str)
        assert var_name in self._var_types.keys(), f'Variable {var_name} does not exists in this context.'
        return self._var_types[var_name]

    def get_variable_state(self, var_name: str) -> Any:
        """Returns the state of a specific variable.

        :param var_name: Variable name.
        :type var_name: str
        :return: Variable state.
        :rtype: Any
        """
        assert isinstance(var_name, str)
        assert var_name in self._var_states.keys(), f'Variable {var_name} does not exists in this context.'
        return self._var_states[var_name]
    
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
                past_context_content['__setattr__'] = _raise_read_only_exception
                
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
            if var_name in self._var_states.keys():
                assert isinstance(var_value, self._var_types[var_name]), f'not allowed assignment of value {var_value} of type {type(var_value)} to variable {var_name} of type {self._var_types[var_name]}.'
                self._var_states[var_name] = var_value
            elif var_name in ('past', 'getattr', 'setattr'):
                raise Exception(f'Attribute {var_name} is a method.')
            else:
                self._aux[var_name] = var_value

        def _get_attribute(contextobj, var_name):
            if var_name == 'past': #call to the past method
                return _get_past_method(contextobj)
            elif var_name == 'getstate': #call to the getstate method
                return _get_getstate_method(contextobj)
            elif var_name == 'setstate': #call to the setstate method
                return _get_setstate_method(contextobj)
            elif var_name in self._var_states.keys(): #get variable state
                return self._var_states[var_name]
            elif var_name in self._aux.keys(): #get aux object
                return self._aux[var_name]
            else:
                raise Exception(f'Attribute {var_name} does not exists in the context.')

        MyContextType = type(f'Context{id(self)}', (ContextType,), {
            '__setattr__': _set_attribute,
            '__getattribute__': _get_attribute
        })

        return MyContextType()

    def _prepare(self):
        """Internal method.
        Calls the simulation beginning callback.
        """
        context = self._get_context_obj()
        self._begin_function(context)

    def _run_step(self, step: int):
        """Internal method.
        Calls the simulation run-step callback.
        Args:
            step (int): step number.
        """
        context = self._get_context_obj()
        self._step_function(context, step)

    def run_steps(self, n: int):
        """Run 'n' steps of the simulation.

        :param n: Number of steps.
        :type n: int
        """
        assert isinstance(n, int)
        assert n > 0

        self._prepare()
        for step in range(n):
            self._run_step(step)
            self._log_states()
            self._steps_taken += 1

    def get_history(self) -> Dict[str, List]:
        """Returns a copy of the historic dictionary.

        :return: historic dictionary in the format {variable_name: variable_history}.
        :rtype: Dict[str, List]
        """
        return {var_name: self._history[var_name].copy() for var_name in self._history.keys()}

    def get_variable_history(self, var_name: str) -> List:
        """Get a copy of the historic of a specific variable.

        :param var_name: variable name.
        :type var_name: str
        :return: variable state history.
        :rtype: List
        """
        assert isinstance(var_name, str), f'Argument of var_name must be string. Given {type(var_name)}.'
        assert var_name in self._history.keys(), f'Variable {var_name} does not exists.'
        return self._history[var_name].copy()

    def get_variable_numpy_history(self, var_name: str) -> np.ndarray:
        """Get the historic of a specific variable as a NumPy array.

        :param var_name: variable's name.
        :type var_name: str
        :return: variable state history.
        :rtype: np.ndarray
        """
        return np.array(self.get_variable_history(var_name))

    def get_history_dataframe(self) -> DataFrame:
        """Get variables history as a Pandas DataFrame.

        :return: historic DataFrame.
        :rtype: DataFrame
        """
        return DataFrame(self._history)
   
    def get_numpy_history(self) -> Dict[str, np.ndarray]:
        """Get variables history as a dictionary of NumPy arrays.

        :return: variables history in the format {variable_name: variable_history}.
        :rtype: Dict[str, np.ndarray]
        """
        return {var_name:np.array(self._history[var_name]) for var_name in self._history.keys()}