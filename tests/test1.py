from pymcsl import SubSimulationEnv

def prepare(context):
    print('---prepare---', type(context))
    context.x = 0.0
    context.y = 0.0

def run_step(context, step):
    print(f'---step {step}---', type(context))
    context.x += 1.0
    context.y -= 1.0
    #context.setstate('x', context.getstate('x') + 1)
    #context.setstate('y', context.getstate('y') - 1)

    if step >= 3:
        print('x', context.x, context.past(1).x, context.past(2).x)
        print('y', context.y, context.past(1).y, context.past(2).y)

if __name__ == '__main__':
    vars = [
        ('x', float, 0.0),
        ('y', float, 0.0)
    ]

    subsim = SubSimulationEnv(vars, prepare, run_step)
    subsim.run_steps(10)
    print(subsim.get_history_dataframe())