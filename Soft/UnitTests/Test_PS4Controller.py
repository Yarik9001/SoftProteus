from pyPS4Controller.controller import Controller

def connect():
    print('hello world')
    # any code you want to run during initial connection with the controller
    pass

def disconnect():
    print('goodbay world')
    # any code you want to run during loss of connection with the controller or keyboard interrupt
    pass

class MyController(Controller):
<<<<<<< HEAD
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
=======

    def __init__(self):
        Controller.__init__(self,interface="/dev/input/js0", connecting_using_ds4drv=False)
>>>>>>> 691da8940b73ccc6f13e72eaa69bad015106477f


controller = MyController()
controller.listen(on_connect=connect, on_disconnect=disconnect)