'''
Filipe Chagas
June-2022
'''

import pymcsl as mcs

env = mcs.MonteCarloSimulationEnv(
    variables=[
        ('x', int, 0)
    ],
    n_subsimulations = 100,
    n_steps = 10
)

LEFT = -1
RIGHT = 1

@env.subsim_begin
def beginf(context):
    context.direction = mcs.DiscreteRandomVariable({
        LEFT: 1,
        RIGHT: 1
    })

@env.subsim_step
def stepf(context, step):
    context.x += context.direction.evaluate()

if __name__ == '__main__':
    env.run()