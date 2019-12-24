
import os

from collections import defaultdict
from pkgutil import iter_modules
from warnings import warn

import pkg_resources

from six import string_types, iteritems
from six.moves.collections_abc import Iterable

from .error import ExtendyError, ExtendyWarning


def listify(value):
    if value is None:
        return []
    if isinstance(value, string_types) or not isinstance(value, Iterable):
        return [value]
    return value


def fqn(clazz):
    return '%s.%s' % (clazz.__module__, clazz.__name__)


class Manager(object):
    """
    An Extension management interface that is responsible for coordinating the
    retrieval of Extension Implementations.
    """

    def __init__(self):
        self._registrations = defaultdict(set)

    def register(self, extension, implementation):
        """
        Registers an implementation of an extension with the manager so that it
        is available for use.

        :param extension: the extension to register the implementation for
        :type extension: extendy.Extension
        :param implementation: the implementation to registry with the manager
        :type implementation: extendy.Extension
        """

        if not self._is_ok(extension, implementation):
            raise ExtendyError(
                '"%s" is not inherited from "%s"' % (
                    fqn(implementation),
                    fqn(extension),
                ),
            )
        self._registrations[extension].add(implementation)

    def unregister(self, extension, implementation):
        """
        Removes an implementation's registration with the manager so that it is
        no longer available for use.

        :param extension: the extension remove the registration from
        :type extension: extendy.Extension
        :param implementation: the implementation to remove
        :type implementation: extendy.Extension
        """

        try:
            self._registrations[extension].remove(implementation)
        except KeyError:
            pass

    def find(
            self,
            extension,
            registered=True,
            entry_points=None,
            paths=None,
            prefixes=None,
            modules=None,
            names=None):
        """
        Returns implementations of the specified extension that are found in
        any number of locations.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :param registered:
            whether or not to include implementations that were explicitly
            registered with this manager; if not specified, defaults to
            ``True``
        :type registered: bool
        :param entry_points: the entry points to search for implementations
        :type entry_points: list(str)
        :param paths: the directories to search for implementations
        :type paths: list(str)
        :param prefixes:
            the prefixes to to match on module names for modules that should
            be searched for implementations
        :type prefixes: list(str)
        :param modules:
            the modules or names of modules to search for implementations
        :type modules: list(str or module)
        :param names: the full-qualified names of implementations to include
        :type names: list(str)
        :rtype: list(extendy.Extension)
        """

        implementations = set()

        if registered:
            implementations.update(self.find_by_registration(extension))

        for entry_point in listify(entry_points):
            implementations.update(
                self.find_by_entry_point(extension, entry_point)
            )

        for path in listify(paths):
            implementations.update(
                self.find_by_path(extension, path)
            )

        for module in listify(modules):
            implementations.update(
                self.find_by_module(extension, module)
            )

        for prefix in listify(prefixes):
            implementations.update(
                self.find_by_module_prefix(extension, prefix)
            )

        for name in listify(names):
            implementations.add(
                self.find_by_name(extension, name)
            )

        return list(implementations)

    def find_by_registration(self, extension):
        """
        Returns implementations of an extension that were actively registered
        with this manager.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :rtype: list(extendy.Extension)
        """

        return list(self._registrations[extension])

    def find_by_entry_point(self, extension, entry_point):
        """
        Returns implementations of an extension that are installed via the
        specified ``setuptools`` entry_point.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :param entry_point: the name of the entry_point to search
        :type entry_point: str
        :rtype: list(extendy.Extension)
        """

        implementations = []

        for entry in pkg_resources.iter_entry_points(entry_point):
            try:
                implementation = entry.load()
            except ImportError as exc:
                warn(
                    'Could not load entry "%s" from "%s" (%s %s): %s' % (
                        entry.name,
                        entry_point,
                        entry.dist.project_name,
                        entry.dist.version,
                        exc,
                    ),
                    ExtendyWarning,
                )
                continue

            if self._is_ok(extension, implementation, quiet=True):
                implementations.append(implementation)

        return implementations

    def find_by_path(self, extension, path):
        """
        Returns implementations of an extension that are found in modules found
        in the specified directory.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :param path: the directory to search
        :type path: str or module
        :rtype: list(extendy.Extension)
        """

        implementations = []

        if path.endswith('/'):
            path = path[:-1]

        if not os.path.exists(path):
            return implementations

        for importer, name, _ in iter_modules([path]):
            module = importer.find_module(name).load_module(name)
            implementations.extend(self.find_by_module(extension, module))

        return implementations

    def find_by_module_prefix(self, extension, prefix):
        """
        Returns implementations of an extension that are found in modules named
        using the specified prefix.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :param prefix: the prefix to match on module names
        :type prefix: str
        :rtype: list(extendy.Extension)
        """

        implementations = []

        for _, name, _ in iter_modules():
            if not name.startswith(prefix):
                continue
            implementations.extend(self.find_by_module(extension, name))

        return implementations

    def find_by_module(self, extension, module):
        """
        Returns implementations of an extension that are found in the specified
        module.

        :param extension: the extension to retrieve implementations for
        :type extension: extendy.Extension
        :param module: the module to search
        :type module: str or module
        :rtype: list(extendy.Extension)
        """

        if isinstance(module, string_types):
            try:
                module = __import__(module, globals(), locals())
            except ImportError as exc:
                warn(
                    'Could not import module "%s": %s' % (
                        module,
                        exc
                    ),
                    ExtendyWarning,
                )
                return []

        implementations = []

        for name, obj in iteritems(module.__dict__):
            if name.startswith('_'):
                continue
            if self._is_ok(extension, obj, quiet=True):
                implementations.append(obj)

        return implementations

    def find_by_name(self, extension, name):
        """
        Returns the specified implementation of an extension.

        :param extension: the extension to retrieve the implementation for
        :type extension: extendy.Extension
        :param name:
            the fully-qualified name of the implementation -- e.g.
            "some.module.ClassName"
        :type name: str
        :rtype: extendy.Extension
        """

        module_name, class_name = name.rsplit('.', 1)
        try:
            module = __import__(module_name, globals(), locals(), class_name)
        except ImportError as exc:
            warn(
                'Could not import module "%s": %s' % (
                    module_name,
                    exc
                ),
                ExtendyWarning,
            )
        else:
            try:
                implementation = getattr(module, class_name)
            except AttributeError as exc:
                warn(
                    'Could not find class "%s" in module "%s"' % (
                        class_name,
                        module_name,
                    ),
                    ExtendyWarning,
                )
            else:
                if self._is_ok(extension, implementation):
                    return implementation

        return None

    def _is_ok(self, extension, implementation, quiet=False):  # noqa: no-self-use
        if not issubclass(implementation, extension):
            if not quiet:
                warn(
                    '"%s" is not inherited from "%s"' % (
                        fqn(implementation),
                        fqn(extension),
                    ),
                    ExtendyWarning,
                )
            return False
        return implementation != extension


#: The default Manager used by Extension.register() if the Extension does not
#: explicitly define a specific one.
GlobalManager = Manager()  # noqa: invalid-name

