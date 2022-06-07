"""
By Filipe Chagas
June-2022
"""

from typing import *
from subsimulation import SubSimulationEnv, ContextType

class MonteCarloSimulationEnv():
    """
    The MonteCarloSimulationEnv class provides a code base to facilitate the implementation of Monte Carlo simulations.
    The MonteCarloSimulationEnv class performs a series of independent subsimulations under the same conditions.
    """
    
    def __init__(self, variables: List[Tuple[str, type, object]], n_subsimulations: int, n_steps: int) -> None:
        """
        :param variables: List of simulation variables in the format [(variable_name, variable_type, default_value)].
        :type variables: List[Tuple[str, type, object]]
        :param n_subsimulations: Number of subsimulations.
        :type n_subsimulations: int
        :param n_steps: Number of steps per subsimulation.
        :type n_steps: int
        """
        assert isinstance(n_subsimulations, int), f'Argument of \'n_subsimulations\' must be integer. Given {type(n_subsimulations)}.'
        assert n_subsimulations > 0, f'n_subsimulations must be positive. Given {n_subsimulations}.'
        assert isinstance(n_steps, int), f'Argument of \'n_steps\' must be integer. Given {type(n_steps)}.'
        assert n_steps > 0, f'n_steps must be positive. Given {n_steps}.'
        assert isinstance(variables, list), f'Argument of \'variables\' must be a list, but a {type(variables)} object was received.'
        assert all([isinstance(var_name, str) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_type, type) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_default, var_type) for var_name, var_type, var_default in variables]), f'Some default value in \'variables\' list does not correspond to its variable\'s type.'
        assert all([var_name not in ('past', 'getstate', 'setstate') for var_name, var_type, var_default in variables]), 'Names \'past\', \'getstate\' and \'setstate\' are internally reserved and forbidden for variables.'
        
        self._variables = variables
        self._n_subsims = n_subsimulations
        self._n_steps = n_steps
        self._subsim_begin_function = None
        self._subsim_step_function = None
        self._subsim_envs = None

    @property
    def subsim_begin(self) -> Callable:
        """Returns a decorator that subscribes a function as the beginning function of all subsimulations.

        :return: Wrapped decorator.
        :rtype: Callable
        """
        def wrapped(function: Callable[[ContextType], None]) -> Callable:
            self._subsim_begin_function = function
            return function
        return wrapped

    @property
    def subsim_step(self) -> Callable:
        """Returns a decorator that subscribes a function as the step-function of all subsimulations.

        :return: Wrapped decorator.
        :rtype: Callable
        """
        def wrapped(function: Callable[[ContextType], None]) -> Callable:
            self._subsim_step_function = function
            return function
        return wrapped

    def set_subsim_begin_callback(self, f: Callable[[ContextType], None]):
        """Subscribes a function as the begin-function of all subsimulations.

        :param f: Callback function.
        :type f: Callable[[ContextType], None]
        """
        assert isinstance(f, Callable)
        self._subsim_begin_function = f
    
    def set_subsim_step_callback(self, f: Callable[[ContextType], None]):
        """Subscribes a function as the step-function of all subsimulations.

        :param f: Callback function.
        :type f: Callable[[ContextType], None]
        """
        assert isinstance(f, Callable)
        self._subsim_step_function = f

    def run(self, show_progress: bool = True):
        """Run all the independent subsimulations.

        :param show_progress: Enable progress bar, defaults to True
        :type show_progress: bool, optional
        """
        assert isinstance(self._subsim_begin_function, Callable), 'Begin callback is not defined.'
        assert isinstance(self._subsim_step_function, Callable), 'Step callback is not defined.'
        
        if show_progress:
            from tqdm import tqdm
        
        self._subsim_envs = [SubSimulationEnv(self._variables, self._subsim_begin_function, self._subsim_step_function) for i in range(self._n_subsims)]
        
        for env in tqdm(self._subsim_envs) if show_progress else self._subsim_envs:
            env.run_steps(self._n_steps)
    
    def get_subsim_env(self, subsim_index: int) -> SubSimulationEnv:
        """Returns the SubSimulationEnv for a specific subsimulation.

        :param subsim_index: subsimulation index (starting at 0).
        :type subsim_index: int
        :return: SubSimulationEnv object.
        :rtype: SubSimulationEnv
        """
        assert subsim_index < self._n_subsims, f'subsim_index must be less than the number of subsimulations.'
        return self._subsim_envs[subsim_index]

    