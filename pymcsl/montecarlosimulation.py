"""
By Filipe Chagas
June-2022
"""

from typing import *
import numpy as np
from subsimulation import SubSimulationEnv, ContextType

def _first_or_default(l: List, f: Callable[[Any], bool], default: Any = None) -> Any:
    for x in l:
        if f(x):
            return x
    return default

class MonteCarloSimulationEnv():
    """
    The MonteCarloSimulationEnv class provides a code base to facilitate the implementation of Monte Carlo simulations.
    The MonteCarloSimulationEnv class performs a series of independent subsimulations under the same conditions.
    """
    
    def __init__(self, variables: List[Tuple[str, type, Union[str, int, float, bool]]], n_subsimulations: int, n_steps: int) -> None:
        """
        :param variables: List of simulation variables in the format [(variable_name, variable_type, default_value)].
        :type variables: List[Tuple[str, type, Union[str, int, float, bool]]]
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
        assert all([var_type in (str, int, float, bool) for var_name, var_type, var_default in variables]), f'variable types must be int, float, str or bool.'
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

    def get_variable_mean(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the mean of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', an average for each step is calculated; if domain='subsim', an average for each subsimulation is calculated, and if domain=None, the overall average is calculated, defaults to 'time'
        :type domain: str, optional
        :return: An array with an average for each domain value (step or subsim), or an overall average.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.mean(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.mean(hist).astype(np.float)

    def get_variable_median(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the median of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a median for each step is calculated; if domain='subsim', a median for each subsimulation is calculated, and if domain=None, the overall median is calculated, defaults to 'time'
        :type domain: str, optional
        :return: An array with a median for each domain value (step or subsim), or an overall median.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.median(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.median(hist).astype(np.float)

    def get_variable_var(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the variance of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a variance for each step is calculated; if domain='subsim', a variance for each subsimulation is calculated, and if domain=None, the overall variance is calculated, defaults to 'step'
        :type domain: str, optional
        :return: An array with a variance for each domain value (step or subsim), or an overall variance.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.var(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.var(hist).astype(np.float)

    def get_variable_std(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the standard deviation of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a standard deviation for each step is calculated; if domain='subsim', a standard deviation for each subsimulation is calculated, and if domain=None, the overall standard deviation is calculated, defaults to 'step'
        :type domain: str, optional
        :return: An array with a standard deviation for each domain value (step or subsim), or an overall standard deviation.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.std(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.std(hist).astype(np.float)

    def get_variable_min(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the minimun of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).
        
        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a minimun for each step is calculated; if domain='subsim', a minimun for each subsimulation is calculated, and if domain=None, the overall minimun is calculated, defaults to 'step'
        :type domain: str, optional
        :return: An array with a minimun for each domain value (step or subsim), or an overall minimun.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.min(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.min(hist).astype(np.float)

    def get_variable_max(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the maximun of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a maximun for each step is calculated; if domain='subsim', a maximun for each subsimulation is calculated, and if domain=None, the overall maximun is calculated, defaults to 'step'
        :type domain: str, optional
        :return: An array with a maximun for each domain value (step or subsim), or an overall maximun.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.max(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.max(hist).astype(np.float)

    def get_variable_sum(self, var_name: str, domain: str = 'step') -> Union[np.ndarray, np.float]:
        """
        Calculates the sum of a variable. 
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param domain: If domain='step', a sum for each step is calculated; if domain='subsim', a sum for each subsimulation is calculated, and if domain=None, the overall sum is calculated, defaults to 'step'
        :type domain: str, optional
        :return: An array with a sum for each domain value (step or subsim), or an overall sum.
        :rtype: Union[np.ndarray, np.float]
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert domain in ('step', 'subsim', None), 'domain must be \'step\', \'subsim\' or None.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.sum(hist, axis=(0 if domain == 'step' else 1)).astype(np.float) if domain != None else np.sum(hist).astype(np.float)

    def get_variable_histogram(self, var_name: str, n_bins: int, density: bool = False) -> np.ndarray:
        """Returns an array with a histogram of the variable for each step of the simulation.
        The 0-axis indexes are the domain values (step indexes or subsim indexes).

        :param var_name: Variable name.
        :type var_name: str
        :param n_bins: Number of bins per histogram.
        :type n_bins: int
        :param density: Set to true so histograms are density instead of counts. defaults to False
        :type density: bool, optional
        :return: Array of histograms.
        :rtype: np.ndarray
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        assert isinstance(n_bins, int), 'n_bins must be int.'
        assert n_bins >= 1, 'n_bins must be greater than 0.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        assert found_type in (float, int, bool), 'Variable type must be int, float or bool.'
    
        vhistories = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        vhistories = np.array(vhistories)
        vmax = np.max(vhistories)
        vmin = np.min(vhistories)

        vhistogram = [np.histogram(vhistories[:,i], bins=n_bins, range=(vmin, vmax), density=density)[0]  for i in range(vhistories.shape[1])]
        return np.array(vhistogram).astype(np.float)

    def get_variable_histories(self, var_name: str) -> np.ndarray:
        """Returns an array with all the outcomes that a variable had throughout the simulation. 
        The 0-axis indices are the subsimulations and the 1-axis indices are the steps.

        :param var_name: Variable name.
        :type var_name: str
        :return: Array with the outcomes of the variable.
        :rtype: np.ndarray
        """
        assert isinstance(var_name, str), 'var_name must be string.'
        found_name, found_type, found_default = _first_or_default(self._variables, lambda t: t[0]==var_name, (None, None, None))
        assert isinstance(found_name, str), f'Variable {var_name} does not exists.'
        
        hist = [self._subsim_envs[i].get_variable_numpy_history(var_name) for i in range(self._n_subsims)]
        return np.array(hist).astype(np.float)
