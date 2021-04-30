from sys import getsizeof
print('None', getsizeof(None))
print('list', getsizeof([]))
print('dikt', getsizeof({}))
print('tuple', getsizeof(tuple()))
class a:
    def __init__(self):
        self.name = 'Proteus0'
        self.n = 1234567
        self.d = {}
        self.l = []
ai = a()
print('class', getsizeof(ai))
 
# измерение размера 
