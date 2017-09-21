from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
standard_library.install_aliases()

import logging
import os
import warnings

import ramrod
from stix.core import STIXPackage
from stix.utils.parser import UnsupportedVersionError

LATEST_STIX_VERSION = "1.2"

class StixSourceItem(object):
    """A base class for STIX package containers."""

    def __init__(self, source_item):
        self.source_item = source_item
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore","The use of this field has been deprecated",UserWarning)
            try:
                self.stix_package = STIXPackage.from_xml(self.io())
            except UnsupportedVersionError:
                updated = ramrod.update(self.io(), to_=LATEST_STIX_VERSION)
                document = updated.document.as_stringio()
                self.stix_package = STIXPackage.from_xml(document)
            except Exception:
                logging.error('error parsing STIX package (%s)', self.file_name())
                self.stix_package = None

        self.stix_version = self.stix_package.version

    def io(self):
        raise NotImplementedError

    def file_name(self):
        raise NotImplementedError

    def save(self, directory):
        file_name = self.file_name()
        full_path = os.path.join(directory, file_name)
        try:
            logging.info('saving STIX package to file \'{}\''.format(full_path))
            with open(full_path, 'wb') as file_:
                file_.write(self.stix_package.to_xml())
        except Exception:
            logging.error('unable to save STIX package to file \'{}\''.format(full_path))
