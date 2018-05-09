import os

import pytest

import extendy_testpkg

from extendy import Extension, Manager, ExtendyError, ExtendyWarning


class TestExtension(Extension):
    def foo(self):
        return 'foo'

class TestImplementation(TestExtension):
    pass

class AnotherTestImplementation(TestExtension):
    def foo(self):
        'bar'

class OtherExtension(Extension):
    pass

class OtherImplementation(OtherExtension):
    pass

class SomeClass(object):
    pass


def test_register():
    man = Manager()

    assert man.find_by_registration(TestExtension) == []

    man.register(TestExtension, TestImplementation)

    assert man.find_by_registration(TestExtension) == [
        TestImplementation,
    ]


def test_register_bad():
    man = Manager()

    assert man.find_by_registration(TestExtension) == []

    with pytest.raises(ExtendyError), pytest.warns(ExtendyWarning):
        man.register(TestExtension, OtherImplementation)
    with pytest.raises(ExtendyError), pytest.warns(ExtendyWarning):
        man.register(TestExtension, SomeClass)

    assert man.find_by_registration(TestExtension) == []


def test_unregister():
    man = Manager()

    assert man.find_by_registration(TestExtension) == []

    man.register(TestExtension, TestImplementation)

    assert man.find_by_registration(TestExtension) == [
        TestImplementation,
    ]

    man.unregister(TestExtension, TestImplementation)

    assert man.find_by_registration(TestExtension) == []

    man.unregister(TestExtension, TestImplementation)
    man.unregister(TestExtension, SomeClass)

    assert man.find_by_registration(TestExtension) == []


def test_by_name():
    man = Manager()

    assert man.find_by_name(extendy_testpkg.FooExtension, 'extendy_testpkg.FooImplementation') == extendy_testpkg.FooImplementation

    with pytest.warns(ExtendyWarning, match='not inherited from'):
        assert man.find_by_name(extendy_testpkg.FooExtension, 'extendy_testpkg.NotAnImplementation') is None

    with pytest.warns(ExtendyWarning, match='Could not import module'):
        assert man.find_by_name(extendy_testpkg.FooExtension, 'some.garbage.module.MyClass') is None

    with pytest.warns(ExtendyWarning, match='Could not find class'):
        assert man.find_by_name(extendy_testpkg.FooExtension, 'extendy_testpkg.DoesNotExist') is None


def test_by_module():
    man = Manager()

    assert sorted(man.find_by_module(extendy_testpkg.FooExtension, 'extendy_testpkg')) == sorted([
        extendy_testpkg.FooImplementation,
        extendy_testpkg.AnotherFooImplementation,
        extendy_testpkg.ThirdFooImplementation,
    ])

    assert sorted(man.find_by_module(extendy_testpkg.FooExtension, extendy_testpkg)) == sorted([
        extendy_testpkg.FooImplementation,
        extendy_testpkg.AnotherFooImplementation,
        extendy_testpkg.ThirdFooImplementation,
    ])


def test_by_module_bad():
    man = Manager()

    with pytest.warns(ExtendyWarning, match='Could not import module'):
        assert man.find_by_module(extendy_testpkg.FooExtension, 'some.garbage.module') == []


def test_by_module_prefix():
    man = Manager()

    assert sorted(man.find_by_module_prefix(extendy_testpkg.FooExtension, 'extendy_testpkg')) == sorted([
        extendy_testpkg.FooImplementation,
        extendy_testpkg.AnotherFooImplementation,
        extendy_testpkg.ThirdFooImplementation,
    ])


def test_by_path():
    man = Manager()

    actual = man.find_by_path(
        extendy_testpkg.FooExtension,
        os.path.join(os.path.dirname(__file__), 'testpkg/src/extendy_testpkg/stuff/'),
    )
    assert sorted([clazz.__name__ for clazz in actual]) == sorted([
        'StuffBar',
        'StuffBaz',
        'StuffFoo',
    ])


def test_by_path_bad():
    man = Manager()

    assert man.find_by_path(extendy_testpkg.FooExtension, '/some/bogus/directory') == []


def test_by_entry_point():
    man = Manager()

    with pytest.warns(ExtendyWarning, match='Could not load entry'):
        assert sorted(man.find_by_entry_point(extendy_testpkg.FooExtension, 'extendytest')) == sorted([
            extendy_testpkg.ThirdFooImplementation,
        ])

    with pytest.warns(ExtendyWarning, match='Could not load entry'):
        assert sorted(man.find_by_entry_point(extendy_testpkg.BarExtension, 'extendytest')) == sorted([
            extendy_testpkg.BarImplementation,
        ])


def test_find():
    man = Manager()

    class RegisteredFoo(extendy_testpkg.FooExtension):
        pass
    extendy_testpkg.FooExtension.register(RegisteredFoo, manager=man)

    assert man.find(extendy_testpkg.FooExtension) == [
        RegisteredFoo,
    ]

    assert man.find(extendy_testpkg.FooExtension, registered=False) == []

    with pytest.warns(ExtendyWarning, match='Could not load entry'):
        assert sorted(man.find(
            extendy_testpkg.FooExtension,
            entry_points='extendytest',
        )) == sorted([
            RegisteredFoo,
            extendy_testpkg.ThirdFooImplementation,
        ])

    actual = sorted(man.find(
        extendy_testpkg.FooExtension,
        paths=[os.path.join(os.path.dirname(__file__), 'testpkg/src/extendy_testpkg/stuff/')],
    ))
    assert sorted([clazz.__name__ for clazz in actual]) == sorted([
        'RegisteredFoo',
        'StuffBar',
        'StuffBaz',
        'StuffFoo',
    ])

    assert sorted(man.find(
        extendy_testpkg.FooExtension,
        modules=extendy_testpkg,
    )) == sorted([
        RegisteredFoo,
        extendy_testpkg.FooImplementation,
        extendy_testpkg.AnotherFooImplementation,
        extendy_testpkg.ThirdFooImplementation,
    ])

    assert sorted(man.find(
        extendy_testpkg.FooExtension,
        prefixes='extendy_',
    )) == sorted([
        RegisteredFoo,
        extendy_testpkg.FooImplementation,
        extendy_testpkg.AnotherFooImplementation,
        extendy_testpkg.ThirdFooImplementation,
    ])

    assert sorted(man.find(
        extendy_testpkg.FooExtension,
        names='extendy_testpkg.AnotherFooImplementation',
    )) == sorted([
        RegisteredFoo,
        extendy_testpkg.AnotherFooImplementation,
    ])

    with pytest.warns(ExtendyWarning, match='Could not load entry'):
        actual = sorted(man.find(
            extendy_testpkg.FooExtension,
            entry_points='extendytest',
            paths=[os.path.join(os.path.dirname(__file__), 'testpkg/src/extendy_testpkg/stuff/')],
            modules=extendy_testpkg,
            prefixes='extendy_',
            names='extendy_testpkg.AnotherFooImplementation',
        ))
    assert sorted([clazz.__name__ for clazz in actual]) == sorted([
        'RegisteredFoo',
        'StuffBar',
        'StuffBaz',
        'StuffFoo',
        'FooImplementation',
        'AnotherFooImplementation',
        'ThirdFooImplementation',
    ])

