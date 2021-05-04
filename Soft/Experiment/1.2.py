class test: 
    def transformation(self, value:int):
        '''
        Функция перевода значений АЦП с джойстика в проценты, где 50 процентов
        дефолтное значение
        '''
        value = (32768 - i) // 655
        return value
    

# test one 
a = test()
for i in range(-32767, 32768):
    print(a.transformation(i))
 