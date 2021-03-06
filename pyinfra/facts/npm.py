# encoding: utf8

# pyinfra
# File: pyinfra/facts/npm.py
# Desc: npm package manager facts

from __future__ import unicode_literals

from pyinfra.api import FactBase

from .util.packaging import parse_packages

# Matching output of npm list
npm_regex = r'^[└├]\─\─\s([a-zA-Z0-9\-]+)@([0-9\.]+)$'


class NpmPackages(FactBase):
    '''
    Returns a dict of installed npm packages globally or in a given directory:

    .. code:: python

        'package_name': 'version',
        ...
    '''

    default = {}
    command = 'npm list -g --depth=0'

    def command(self, directory=None):
        if directory:
            return 'cd {0} && npm list -g --depth=0'.format(directory)
        else:
            return 'npm list -g --depth=0'

    def process(self, output):
        parse_packages(npm_regex, output)
