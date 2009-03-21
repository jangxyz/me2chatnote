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

def find_all_test_files(filename_arg='*'):
    """ finds files that end with '_test.py', recursively """
    #test_file_pattern = re.compile('^t(est)?_.*\.py$')
    test_file_pattern = re.compile('.*_test\.py$')
    is_test = lambda filename: test_file_pattern.match(filename)
    drop_dot_py = lambda filename: filename[:-3]
    join_module = lambda *names: '.'.join(names) if len(filter(None, names)) > 1 else names[-1]
    #return [drop_dot_py(module) for module in filter(is_test, os.listdir(os.curdir))]
    check_filename = True if os.path.isfile(filename_arg) else False
    modules = []
    for root, dirs, files in os.walk(os.curdir):
        root_name = os.path.split(root)[-1].lstrip('.')
        if check_filename:
            files = filter(lambda x: x == filename_arg, files)
        for test_file in filter(is_test, files):
            modules.append(join_module(root_name, drop_dot_py(test_file)))
        #modules += ['.'.join([root_name, drop_dot_py(test_file)]) for test_file in filter(is_test, files)]
    return modules


def suite():
    sys.path.append(os.curdir)

    arg_len = len(sys.argv)
    filename_arg = sys.argv[1]                    if arg_len >= 2  else '*'
    testcase_arg, testmethod_arg = sys.argv[2:4]  if arg_len >= 4  else None, None

    loader = unittest.TestLoader()
    if testcase_arg and testmethod_arg:
        dotted_testcase_name = "%s.%s.%s" % (filename_arg, testcase_arg, testmethod_arg)
        loaded_tests = [loader.loadTestsFromName(dotted_testcase_name)]
    else:
        modules_to_test = find_all_test_files(filename_arg)
        print 'Testing', ', '.join(modules_to_test)
        loaded_tests = loader.loadTestsFromNames(modules_to_test)

    alltests = unittest.TestSuite()
    alltests.addTests(loaded_tests)

    return alltests

if __name__ == '__main__':
    try:
        import testoob
        testoob.main(defaultTest='suite')
    except ImportError:
        unittest.main(defaultTest='suite')


