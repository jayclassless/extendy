
from extendy import Extension


class FooExtension(Extension):
    pass

class FooImplementation(FooExtension):
    pass

class AnotherFooImplementation(FooExtension):
    pass

class ThirdFooImplementation(FooExtension):
    pass


class BarExtension(Extension):
    pass

class BarImplementation(BarExtension):
    pass


class NotAnImplementation(object):
    pass

