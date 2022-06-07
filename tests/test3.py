"""
By Filipe Chagas
June-2022
"""

from typing import *
from enum import Enum
from pymcsl import MonteCarloSimulationEnv, SimpleMarkovChain

env = MonteCarloSimulationEnv([('x', int, 0)], 10, 10)

STATE1 = 0
STATE2 = 1
STATE3 = 2

@env.subsim_begin
def beginf(context):
    context.chain = SimpleMarkovChain(
        states = [STATE1, STATE2, STATE3],
        transitions = [
            (STATE1, STATE2, 1),
            (STATE2, STATE1, 1),
            (STATE2, STATE3, 1),
            (STATE3, STATE1, 1)
        ],
        initial_state = STATE1
    )

    context.x = context.chain.state

@env.subsim_step
def stepf(context, step):
    context.chain.foward()
    context.x = context.chain.state

if __name__ == '__main__':
    env.run()
    for i in range(10):
        print(f'---subsimulation {i}---')
        print(env._subsim_envs[i].get_history_dataframe())