from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import contextlib
import csv
import io

from .base import StixTransform


class StixTextTransform(StixTransform):
    """A transform for converting a STIX package to simple text.

    This class and its subclasses implement the :py:func:`text` class method
    which returns a string representation of the STIX package.
    The entire text output may optionally be preceded by a header string.
    Typically, each line of the output will contain details for a particular
    Cybox observable.
    Output is grouped by observable type.
    Each group of observables (by type) may also contain an additional header
    string.

    Args:
        package: the STIX package to transform
        separator: the delimiter used in text output
        include_header: a boolean value indicating whether
            or not headers should be included in the output
        header_prefix: a string prepended to each header row

    Attributes:
        HEADER_LABELS: a list of field names that are printed by the
            :py:func:`header` function.

        OBJECT_HEADER_LABELS: a dict, keyed by object type, containing
            field names associated with an object type. These are printed
            by the :py:func:`header_for_object_type` function.
    """

    HEADER_LABELS = []
    OBJECT_HEADER_LABELS = {}

    def __init__(self, package, default_title=None, default_description=None,
                 default_tlp=u'AMBER', separator=u'|', include_header=True,
                 header_prefix=u'#'):
        super(StixTextTransform, self).__init__(
            package, default_title, default_description, default_tlp,
        )
        self.separator = unicode(separator)
        self.include_header = include_header
        self.header_prefix = unicode(header_prefix)

    # ##### Properties

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, separator):
        self._separator = u'' if separator is None else unicode(separator)

    @property
    def include_header(self):
        return self._include_header

    @include_header.setter
    def include_header(self, include_header):
        self._include_header = bool(include_header)

    @property
    def header_prefix(self):
        return self._header_prefix

    @header_prefix.setter
    def header_prefix(self, header_prefix):
        if header_prefix is None:
            self._header_prefix = u''
        else:
            self._header_prefix = unicode(header_prefix)

    # ##### Class helper methods

    def quote_strings_containing_seperators(self, item):
        """returns an item, quoting it when it contains the delimiter."""
        if self.separator.decode('utf-8') in item.decode('utf-8'):
            return u'"' + unicode(item) + u'"'
        else:
            return unicode(item)

    def join(self, items):
        """str.join, but with quoting when the items contain delimiters."""
        #with io.BytesIO() as csv_stream:
        #    csv.writer(csv_stream, delimiter=self.separator.encode('utf-8')).writerow(items)
        #    return csv_stream.getvalue().strip()
        return unicode(self.separator.join(self.quote_strings_containing_seperators(item) for item in items))

    # ##### Overridden class methods

    def header(self):
        """Returns a header string to display with transform."""
        if self.HEADER_LABELS:
            return unicode('{} {}\n'.format(
                self.header_prefix,
                self.join(self.HEADER_LABELS),
            ))
        else:
            return u''

    def header_for_object_type(self, object_type):
        """Returns a header string associated with an object type."""
        if object_type in self.OBJECT_HEADER_LABELS:
            return unicode('{} {}\n'.format(
                self.header_prefix,
                self.join(self.OBJECT_HEADER_LABELS[object_type]),
            ))
        else:
            return u''

    def text_for_fields(self, fields, object_type):
        """Returns a string representing the given object fields."""
        field_values = []
        if self.OBJECT_FIELDS and object_type in self.OBJECT_FIELDS:
            for field in self.OBJECT_FIELDS[object_type]:
                field_value = unicode(fields[field]) if field in fields else u'None'
                field_values.append(field_value)
        return self.join(field_values)

    def text_for_observable(self, observable, object_type):
        """Returns a string representing the given observable."""
        text = u''
        for field in observable['fields']:
            text += self.text_for_fields(field, object_type) + '\n'
        return unicode(text)

    def text_for_object_type(self, object_type):
        """Returns a string representing observables of the given type."""
        text = u''
        if object_type in self.observables:
            for observable in self.observables[object_type]:
                text += self.text_for_observable(observable, object_type)
        return unicode(text)

    def text(self):
        """Returns a string representation of the STIX package."""
        text = self.header() if self.include_header else u''

        if self.OBJECT_FIELDS:
            object_types = self.OBJECT_FIELDS.keys()
        else:
            object_types = self.observables.keys()
        for object_type in sorted(object_types):
            object_text = self.text_for_object_type(object_type)
            if object_text:
                if self.include_header:
                    text += self.header_for_object_type(object_type)
                text += object_text
        return unicode(text,'utf-8')
