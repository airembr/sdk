from airembr.sdk.common.singleton import Singleton

def test_singleton():
    class MyClass(metaclass=Singleton):
        def __init__(self):
            self.value = 42
    
    instance1 = MyClass()
    instance2 = MyClass()
    
    assert instance1 is instance2
    instance1.value = 100
    assert instance2.value == 100

def test_singleton_with_args():
    # Note: Singleton implementation in this project only uses args for the FIRST call
    class AnotherClass(metaclass=Singleton):
        def __init__(self, val):
            self.val = val
    
    a = AnotherClass(1)
    b = AnotherClass(2)
    
    assert a is b
    assert b.val == 1
