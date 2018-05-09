
import pytest

from extendy import Extension, abstractmethod, abstractproperty, Manager


def test_basic():
    class TestExtension(Extension):
        def test1(self):
            return 'TestExtension'

        @property
        def test2(self):
            return 'TestExtension'

        @abstractmethod
        def test3(self):
            return 'TestExtension'

        @abstractproperty
        def test4(self):
            return 'TestExtension'

    class TestImplementation(TestExtension):
        def test3(self):
            return 'TestImplementation'

        @property
        def test4(self):
            return 'TestImplementation'

    test = TestImplementation()
    assert test.test1() == 'TestExtension'
    assert test.test2 == 'TestExtension'
    assert test.test3() == 'TestImplementation'
    assert test.test4 == 'TestImplementation'


def test_missing_method():
    class TestExtension(Extension):
        @abstractmethod
        def test3(self):
            return 'TestExtension'

    class TestImplementation(TestExtension):
        pass

    with pytest.raises(TypeError):
        test = TestImplementation()


def test_missing_property():
    class TestExtension(Extension):
        @abstractproperty
        def test4(self):
            return 'TestExtension'

    class TestImplementation(TestExtension):
        pass

    with pytest.raises(TypeError):
        test = TestImplementation()


def test_register():
    man = Manager()

    class TestExtension(Extension):
        manager = man

    class TestImplementation(TestExtension):
        pass

    assert man.find(TestExtension) == []

    TestExtension.register(TestImplementation)

    assert man.find(TestExtension) == [TestImplementation]

