
import abc

from six import add_metaclass

from .manager import GlobalManager


@add_metaclass(abc.ABCMeta)
class Extension(object):
    """
    The base class for Extensions that can be used with the extendy framework.
    """

    #: The default extendy.Manager instance to use. If not specified, the
    #: GlobalManager is used.
    manager = GlobalManager

    @classmethod
    def register(cls, implementation, manager=None):
        """
        Registers the specified class as an implementation of this Extension.

        :param implementation:
            the class to register as an implementation of this Extension
        :type implementation: class
        :param manager:
            the Manager to register the class with; if not specified, defaults
            to the Manager defined on this Extension's ``manager`` property
        :type manager: extendy.Manager
        """

        manager = manager or cls.manager
        manager.register(cls, implementation)

