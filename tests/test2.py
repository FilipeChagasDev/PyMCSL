import sys
sys.path.append('./lib')

import montecarlosimulation as mcs

env = mcs.MonteCarloSimulationEnv([('x', int, 0)],10,10)

@env.subsim_begin()
def beginf(context):
    context.x = 0

@env.subsim_step()
def stepf(context, step):
    context.x += 1

if __name__ == '__main__':
    env.run()
    for i in range(10):
        print(f'---subsimulation {i}---')
        print(env._subsim_envs[i].get_history_dataframe())
