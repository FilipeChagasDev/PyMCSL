data = {
    'name': 'Filipe'
}

def pset(self, name, value):
    print('set', name, value)
    data[name] = value

def pget(self, name):
    print('get', name)
    return data[name]

def sayhello(self):
    print('hello')

NameProp = type('NameProp', (object,), {
    '__getattribute__': pget,
    '__setattr__': pset,
    'sayhello': sayhello
})