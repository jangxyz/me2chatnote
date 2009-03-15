#!/usr/bin/env python
# 
# This script is based on the one found at http://vim.wikia.com/wiki/VimTip280
# but has been generalised. It searches the current working directory for
# t_*.py or test_*.py files and runs each of the unit-tests found within.
#
# When run from within Vim as its 'makeprg' with the correct 'errorformat' set,
# any failure will deliver your cursor to the first line that breaks the unit
# tests.
#
# Place this file somewhere where it can be run, such as ${HOME}/bin/alltests.py
# 

import unittest, sys, os, re

def find_all_test_files():
        t_py_re = re.compile('^t(est)?_.*\.py$')
        is_test = lambda filename: t_py_re.match(filename)
        drop_dot_py = lambda filename: filename[:-3]
        return [drop_dot_py(module) for module in filter(is_test, os.listdir(os.curdir))]


def suite():
        sys.path.append(os.curdir)

        modules_to_test = find_all_test_files()
        print 'Testing', ', '.join(modules_to_test)

        alltests = unittest.TestSuite()
        for module in map(__import__, modules_to_test):
                alltests.addTest(unittest.findTestCases(module))

        return alltests

if __name__ == '__main__':
        unittest.main(defaultTest='suite')

