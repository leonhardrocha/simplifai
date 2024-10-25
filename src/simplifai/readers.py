""" Readers for reading data. """

import logging
import abc
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, List, Tuple
import PIL.Image
from timm.data.readers import reader


logger = logging.getLogger(__name__)


class IteratableCollection(Iterable):
    """Base class that allows calling from a iterable collection"""

    def __init__(self, iterable: Iterable):
        """
        Initializes the object with the given iterable.

        Args:
            iterable (Iterable): The iterable to be used with the reader.

        """
        super().__init__()
        self.iterable = iterable
        self.iterator = iter(iterable)

    def __iter__(self):
        """
        Returns an iterator object that iterates over the elements of the iterable passed to the constructor.

        :return: An iterator object that iterates over the elements of the iterable.
        :rtype: iterator
        """
        return self.iterator

    def __next__(self):
        """
        Returns the item from the iterator and increments the iterator.
        """
        return next(self.iterator)

    def __current__(self):
        """
        Returns the next item from the iterator.
        """
        _current = self.iterator
        _next = self.__next__()
        self.iterator = _current
        return _next

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Return the generator that returns the current item in the iteration
          and then calls it with the given arguments and keyword arguments.

        Args:
            *args: Variable length argument list.
            **kwds: Arbitrary keyword arguments.

        Returns:
            Any: The result of calling the current item in the iteration with the
              provided arguments and keyword arguments.
        """
        yield self.__next__().__call__(*args, **kwds)


class SequenceCollection(IteratableCollection, Sequence):
    """Base reader that stores a sequence of data"""

    def __init__(self, sequence: Sequence, lazy: bool = True):
        """
        Initializes the SequenceCollection object.

        Args:
            sequence (Sequence): The sequence to be stored.
            lazy (bool, optional): Flag to determine if lazy loading is enabled. Defaults to True.

        Returns:
            None
        """
        super().__init__(sequence)
        self.sequence = (
            sequence if lazy and not isinstance(sequence, List) else list(sequence)
        )

    def __getitem__(self, index):
        return self.sequence[index]

    def __len__(self) -> int:
        return len(self.sequence)


class FileReaderInterface(metaclass=abc.ABCMeta):
    """
    An abstract class that defines the interface for a file reader.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        """
        A class method that checks if the given subclass is a subclass of the class it is defined on.
        It does this by checking if the subclass has an attribute named 'get_filename' and if it is callable.

        :param cls: The class object.
        :type cls: type
        :param subclass: The subclass to check.
        :type subclass: type
        :return: True if the subclass is a subclass of the class it is defined on and has an attribute named '_filename'
          and it is callable, False otherwise.
        :rtype: bool
        """
        return (hasattr(subclass, 'get_filename') and callable(subclass.get_filename))


@FileReaderInterface.register
class FileNameReader(SequenceCollection, reader.Reader):
    """Mixin of custom collection and Reader that reads filenames from a sequence"""

    def __init__(
        self, sequence: Sequence, basename: bool = False, absolute: bool = False
    ):
        """
        Initializes the FileNameReader object.

        Args:
            sequence (Sequence): The filename sequence to be read.
            basename (bool, optional): Whether to extract the basename of the file. Defaults to False.
            absolute (bool, optional): Whether to return the absolute path of the file. Defaults to False.

        Returns:
            None
        """
        super().__init__(sequence)
        self.basename = basename
        self.absolute = absolute

    def __getitem__(self, index):
        return self.filenames(self.basename, self.absolute)[index]

    def _filename(self, index, basename=False, absolute=False):
        """
        Returns the filename at the specified index in the sequence.

        :param index: The index of the filename in the sequence.
        :type index: int
        :param basename: Whether to extract the basename of the file. Defaults to False.
        :type basename: bool
        :param absolute: Whether to return the absolute path of the file. Defaults to False.
        :type absolute: bool
        :return: The filename at the specified index.
        :rtype: Path
        """
        filename = Path(self.sequence[index])
        if basename:
            filename = filename.parts[-1]
        elif not absolute:
            filename = filename.absolute()
        return filename

    def get_filename(self, index):
        """Returns the filename at the specified index in the sequence without the path"""
        return self[index]


class ImageReader(FileNameReader):
    """Custom reader that reads images from a sequence of filenames"""

    def __init__(self, sequence: Sequence, colortype: str = "RGB"):
        """
        Initializes an instance of the class.

        Args:
            sequence (Sequence): The filename of image sequence to be read.
            colortype (str, optional): The color type of the image. Defaults to "RGB".
        """
        super().__init__(sequence)
        self.colortype = colortype

    def __getitem__(self, index):
        filename = self.sequence[index]
        img = PIL.Image.open(filename).convert(self.colortype)
        return img

    def __len__(self) -> int:
        return len(self.sequence)


class LabelReader(FileNameReader):
    """Custom reader that reads labels from a sequence using a specified function"""

    def __init__(self, sequence: Sequence, func, *args, **kwargs):
        """
        Initializes the LabelReader object.

        Args:
            sequence (Sequence): The sequence from which the labels are to be read.
            func: The function to be applied to each element of the sequence.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        assert isinstance(sequence, List)
        super().__init__(sequence)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __getitem__(self, index):
        filename = str(self.sequence[index])
        return self.func(filename, *self.args, **self.kwargs)
  
    def __func_call__(self, *args: Any, **kwds: Any) -> Any:
        filename = super().__call__(*args, **kwds)
        return self.func(filename, *args, **kwds)


class TupleSequence(IteratableCollection):
    """Custom reader that allows reading from multiple input sequences in a tuple format"""

    def __init__(self, *inputs: Iterable[Tuple[IteratableCollection]]):
        """
        Initializes a TupleReader object with a variable number of input tuples.

        Args:
            *inputs (List[Tuple[Sequence]]): A variable number of input tuples, where each tuple contains a sequence.

        Returns:
            None
        """
        super().__init__(inputs)
        self.inputs = inputs

    def __getitem__(self, index):
        def lazy_get(x):
            return x[index]

        return tuple(map(lazy_get, self.inputs))

    def __len__(self) -> int:
        return min(map(lambda x: x.__len__(), self.inputs))


class RepetableReader(SequenceCollection, Sequence):
    """Custom reader that allows reading from a iterable and repeating it a specified number of times"""

    def __init__(self, sequence: Sequence, repeats: int = 1):
        """
        Initializes an instance of the class.

        Args:
            sequence (Sequence): The sequence to be used in repetition.
            repeats (int, optional): The number of repeats. Defaults to 1.
        """
        super().__init__(sequence)
        self.repeats = repeats
        self.current = 0

    def __len__(self) -> int:
        """
        Returns the length of the sequence multiplied by the number of repeats.

        Returns:
            int: The total length of the sequence repeated the specified number of times.
        """
        return len(self.sequence) * self.repeats

    def __getitem__(self, index) -> Any:
        if index >= len(self):
            raise IndexError()
        self.current = (index * self.repeats) % len(self.sequence)
        return super().__getitem__(self.current)
