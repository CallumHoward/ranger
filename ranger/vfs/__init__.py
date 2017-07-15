# This file is part of ranger, the console file manager.
# License: GNU GPL version 3, see the file "AUTHORS" for details.
"""
ranger's Virtual File System module, a FS abstraction layer
"""

from os.path import abspath, basename


class BaseFile(object):
    possible_file_types = ['unknown']

    def __init__(self, path):
        self.metadata = Metadata()
        self.path = abspath(path)
        self.basename = basename(path)

    def get_info_string(self):
        return 'n/a'

    @property
    def modification_time(self):
        return self.metadata.get('st_mtime', 0)


class ValueUnusable(object):
    """Base class of enum-like classes to denote unusable metadata"""


class ValueUnknown(ValueUnusable):
    """Denotes values which have not been retrieved yet"""


class ValueInaccessible(ValueUnusable):
    """Denotes values which could not be retrieved"""


class ValueUnhandled(ValueUnusable):
    """Denotes values are valid but not handled by the code"""


class ValueInvalid(ValueUnusable):
    """Denotes values were obtained successfully but seem to be invalid"""


class ValueNotApplicable(ValueUnusable):
    """Denotes that in this particular case, a value would make no sense"""


UNUSABLE = (ValueUnusable, ValueUnknown, ValueInaccessible, ValueUnhandled,
            ValueInvalid, ValueNotApplicable)


class Metadata(object):
    """
    A container for all metadata attributes of a vfs-file

    Every File object will have a Metadata object as an attribute.

    Special care must be taken with Metadata objects, for their properties may
    have "unusable" types which have to be checked for before use.

    I.e. instead of:
        if metadata.st_mtime + 10 < time.time():
    You need to write:
        if metadata.st_mtime not in UNUSABLE and \
                metadata.st_mtime + 10 < time.time():
    Because st_mtime may be ValueNotApplicable, which can not be added.

    Instead of:
        if metadata.link_target_exists:
    You need to write:
        if metadata.link_target_exists == True:
    Because it may be ValueUnknown which would evaluate to True.

    The purpose of this is to represent different states and different results
    of the loading process.  So, always assume that Metadata attributes could
    be unusable and validate them!

    >>> metadata = Metadata()
    >>> metadata.size.__name__
    'ValueUnknown'
    >>> metadata.get('size', '???')
    '???'
    >>> metadata.size = 42
    >>> metadata.get('size', '???')
    42
    """
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.file_exists = ValueUnknown
        self.filetype = ValueUnknown
        self.is_link = ValueUnknown
        self.link_target_exists = ValueUnknown
        self.path = ValueUnknown
        self.size = ValueUnknown
        self.st_atime = ValueUnknown
        self.st_ctime = ValueUnknown
        self.st_mode = ValueUnknown
        self.st_mtime = ValueUnknown
        self.st_size = ValueUnknown

    def get(self, attribute_name, fallback_value=None):
        """
        Get an attribute, using a fallback value in case the value is unusable.
        """

        value = getattr(self, attribute_name)
        if isinstance(value, type) and issubclass(value, ValueUnusable):
            return fallback_value
        return value


if __name__ == '__main__':
    import doctest
    doctest.testmod()