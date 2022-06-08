'''
Filipe Chagas
June-2022
'''

import pymcsl as mcs

env = mcs.MonteCarloSimulationEnv(
    variables=[
        ('x', int, 0)
    ],
    n_subsimulations = 1000,
    n_steps = 100
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
    from matplotlib import pyplot as plt
    env.run()
    for i in range(1000):
        h = env.get_subsim_env(i).get_variable_numpy_history('x')
        plt.plot(h)
    plt.show()

    plt.plot(env.get_variable_mean('x'), label='mean')
    plt.plot(env.get_variable_median('x'), label='median')
    plt.plot(env.get_variable_std('x'), label='std')
    plt.plot(env.get_variable_var('x'), label='var')
    plt.plot(env.get_variable_min('x'), label='min')
    plt.plot(env.get_variable_max('x'), label='max')
    plt.plot(env.get_variable_sum('x'), label='sum')
    plt.legend()
    plt.show()

    plt.imshow(env.get_variable_histogram('x', 40, density=True), cmap='hot')
    plt.show()

    print(env.get_variable_histories('x'))