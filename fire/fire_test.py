# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the fire module."""

import os
import sys

import fire
from fire import test_components as tc
from fire import testutils

import mock
import six


class FireTest(testutils.BaseTestCase):

  def testFire(self):
    """Test the Fire function with various test cases.

    This function tests the Fire function by calling it with different test
    cases. It uses mock to patch the sys.argv with 'progname' and then calls
    Fire with different classes. It also tests passing commands as both
    sequences and strings.

    Args:
        self: The test class instance.
    """

    with mock.patch.object(sys, 'argv', ['progname']):
      fire.Fire(tc.Empty)
      fire.Fire(tc.OldStyleEmpty)
      fire.Fire(tc.WithInit)
    # Test both passing command as a sequence and as a string.
    self.assertEqual(fire.Fire(tc.NoDefaults, command='triple 4'), 12)
    self.assertEqual(fire.Fire(tc.WithDefaults, command=('double', '2')), 4)
    self.assertEqual(fire.Fire(tc.WithDefaults, command=['triple', '4']), 12)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults,
                               command=['double', '2']), 4)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults,
                               command=['triple', '4']), 12)

  def testFirePositionalCommand(self):
    """Test passing command as a positional argument.

    This function tests the behavior of the Fire method when the command is
    passed as a positional argument.

    Args:
        self: The instance of the test case.
    """

    # Test passing command as a positional argument.
    self.assertEqual(fire.Fire(tc.NoDefaults, 'double 2'), 4)
    self.assertEqual(fire.Fire(tc.NoDefaults, ['double', '2']), 4)

  def testFireInvalidCommandArg(self):
    """Test that ValueError is raised when an invalid command argument is
    provided to the Fire function.

    This test case checks that a ValueError is raised when an invalid
    command argument is passed to the Fire function.
    """

    with self.assertRaises(ValueError):
      # This is not a valid command.
      fire.Fire(tc.WithDefaults, command=10)

  def testFireDefaultName(self):
    """Test the default behavior of the Fire command line interface.

    This function sets up a mock environment to simulate running the Fire
    command line interface with a default name. It then asserts that the
    output matches the expected stdout pattern and does not produce any
    stderr output.

    Args:
        self: The test case instance.
    """

    with mock.patch.object(sys, 'argv',
                           [os.path.join('python-fire', 'fire',
                                         'base_filename.py')]):
      with self.assertOutputMatches(stdout='SYNOPSIS.*base_filename.py',
                                    stderr=None):
        fire.Fire(tc.Empty)

  def testFireNoArgs(self):
    """Test the Fire function with no arguments provided.

    This test case checks the behavior of the Fire function when called with
    no arguments.
    """

    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['ten']), 10)

  def testFireExceptions(self):
    """Test the exceptions raised by the Fire library.

    This function tests the exceptions raised by the Fire library when
    certain conditions are met.
    """

    # Exceptions of Fire are printed to stderr and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.Empty, command=['nomethod'])  # Member doesn't exist.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.NoDefaults, command=['double'])  # Missing argument.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.TypedProperties, command=['delta', 'x'])  # Missing key.

    # Exceptions of the target components are still raised.
    with self.assertRaises(ZeroDivisionError):
      fire.Fire(tc.NumberDefaults, command=['reciprocal', '0.0'])

  def testFireNamedArgs(self):
    """Test the Fire command with named arguments.

    This function tests the Fire command with named arguments for different
    functions and checks the expected output.

    Args:
        self: The object instance of the test case.
    """

    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '--count', '5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '--count', '5']), 15)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['double', '--count', '5']),
        10)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['triple', '--count', '5']),
        15)

  def testFireNamedArgsSingleHyphen(self):
    """Test the functionality of using single hyphen named arguments in Fire
    commands.

    This function tests the behavior of Fire commands when using single
    hyphen named arguments. It asserts the expected output of the Fire
    commands with different arguments.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '-count', '5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '-count', '5']), 15)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['double', '-count', '5']),
        10)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['triple', '-count', '5']),
        15)

  def testFireNamedArgsWithEquals(self):
    """Test the Fire function with named arguments using equals sign.

    This function tests the Fire function by passing named arguments with
    equals sign to the WithDefaults class and asserts the expected output.

    Args:
        self: The test case object.
    """

    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '--count=5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '--count=5']), 15)

  def testFireNamedArgsWithEqualsSingleHyphen(self):
    """Test the functionality of using named arguments with single hyphen and
    equals sign.

    This function tests the behavior of the Fire method when using named
    arguments with a single hyphen and equals sign.

    Args:
        self: The object instance.
    """

    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '-count=5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '-count=5']), 15)

  def testFireAllNamedArgs(self):
    """Test the Fire function with all named arguments.

    This function tests the Fire function with various combinations of named
    arguments to ensure that the correct output is returned for each
    scenario.

    Args:
        self: The test case object.
    """

    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum', '1', '2']), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--alpha', '1', '2']), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--beta', '1', '2']), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '1', '--alpha', '2']), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '1', '--beta', '2']), 5)
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '1', '--beta', '2']), 5)
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--beta', '1', '--alpha', '2']), 4)

  def testFireAllNamedArgsOneMissing(self):
    """Test the Fire function with all named arguments except one missing.

    This function tests the Fire function with different combinations of
    named arguments being provided and missing. It asserts the output of the
    Fire function for each test case.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum']), 0)
    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum', '1']), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--alpha', '1']), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--beta', '2']), 4)

  def testFirePartialNamedArgs(self):
    """Test the Fire method with partial named arguments.

    This function tests the Fire method with partial named arguments by
    passing different combinations of arguments to the method and asserting
    the expected output.

    Args:
        self: The object instance.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '1', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '1', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--beta', '1', '2']), (2, 1))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '1', '--alpha', '2']), (2, 1))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '1', '--beta', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--alpha', '1', '--beta', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--beta', '1', '--alpha', '2']), (2, 1))

  def testFirePartialNamedArgsOneMissing(self):
    """Test the behavior of Fire when partial named arguments are missing.

    This function tests the behavior of the Fire library when partial named
    arguments are missing. It checks if errors are written to standard
    output and a FireExit exception is raised in different scenarios.
    """

    # Errors are written to standard out and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults,
                command=['identity'])  # Identity needs an arg.

    with self.assertRaisesFireExit(2):
      # Identity needs a value for alpha.
      fire.Fire(tc.MixedDefaults, command=['identity', '--beta', '2'])

    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '1']), (1, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '--alpha', '1']),
        (1, '0'))

  def testFireAnnotatedArgs(self):
    """Test the Fire function with annotated arguments.

    This function tests the Fire function by passing in annotated arguments
    for 'double' and 'triple' commands.

    Args:
        self: The object instance.
    """

    self.assertEqual(fire.Fire(tc.Annotations, command=['double', '5']), 10)
    self.assertEqual(fire.Fire(tc.Annotations, command=['triple', '5']), 15)

  @testutils.skipIf(six.PY2, 'Keyword-only arguments not in Python 2.')
  def testFireKeywordOnlyArgs(self):
    """Test the functionality of keyword-only arguments in the Fire library.

    This function tests the behavior of keyword-only arguments in the Fire
    library by using different commands.

    Args:
        self: The instance of the test case.
    """

    with self.assertRaisesFireExit(2):
      # Keyword arguments must be passed with flag syntax.
      fire.Fire(tc.py3.KeywordOnly, command=['double', '5'])

    self.assertEqual(
        fire.Fire(tc.py3.KeywordOnly, command=['double', '--count', '5']), 10)
    self.assertEqual(
        fire.Fire(tc.py3.KeywordOnly, command=['triple', '--count', '5']), 15)

  def testFireProperties(self):
    """Test the Fire function with different commands.

    This function tests the Fire function with different commands to ensure
    it behaves as expected.
    """

    self.assertEqual(fire.Fire(tc.TypedProperties, command=['alpha']), True)
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['beta']), (1, 2, 3))

  def testFireRecursion(self):
    """Test the recursion functionality of the fire module.

    This function tests the recursion feature of the fire module by calling
    the Fire function with different commands.

    Args:
        self: The object instance of the test case.
    """

    self.assertEqual(
        fire.Fire(tc.TypedProperties,
                  command=['charlie', 'double', 'hello']), 'hellohello')
    self.assertEqual(fire.Fire(tc.TypedProperties,
                               command=['charlie', 'triple', 'w']), 'www')

  def testFireVarArgs(self):
    """Test the VarArgs class in the Fire library by passing a list of strings
    and checking the output.

    This function tests the VarArgs class in the Fire library by passing a
    list of strings as input and checking the output.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(
        fire.Fire(tc.VarArgs,
                  command=['cumsums', 'a', 'b', 'c', 'd']),
        ['a', 'ab', 'abc', 'abcd'])
    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['cumsums', '1', '2', '3', '4']),
        [1, 3, 6, 10])

  def testFireVarArgsWithNamedArgs(self):
    """Test the Fire function with variable arguments and named arguments.

    This function tests the behavior of the Fire function when using
    variable arguments along with named arguments.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['varchars', '1', '2', 'c', 'd']),
        (1, 2, 'cd'))
    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['varchars', '3', '4', 'c', 'd', 'e']),
        (3, 4, 'cde'))

  def testFireKeywordArgs(self):
    """Test the Fire function with keyword arguments.

    This function tests the Fire function with various keyword arguments
    provided in different formats.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--name', 'David', '--age', '24']),
        {'name': 'David', 'age': 24})
    # Run this test both with a list command and a string command.
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--message',
                     '"This is a message it has -- in it"']),  # Quotes stripped
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--message',
                     'This is a message it has -- in it']),
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command='props --message "This is a message it has -- in it"'),
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(tc.Kwargs,
                  command=['upper', '--alpha', 'A', '--beta', 'B']),
        'ALPHA BETA')
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['upper', '--alpha', 'A', '--beta', 'B', '-', 'lower']),
        'alpha beta')

  def testFireKeywordArgsWithMissingPositionalArgs(self):
    """Test the behavior of Fire when keyword arguments are provided without
    all positional arguments.

    This function tests the behavior of the Fire library when keyword
    arguments are provided without all the required positional arguments.
    """

    self.assertEqual(
        fire.Fire(tc.Kwargs, command=['run', 'Hello', 'World', '--cell', 'is']),
        ('Hello', 'World', {'cell': 'is'}))
    self.assertEqual(
        fire.Fire(tc.Kwargs, command=['run', 'Hello', '--cell', 'ok']),
        ('Hello', None, {'cell': 'ok'}))

  def testFireObject(self):
    """Test the FireObject function by checking the output of different
    commands.

    This function tests the FireObject function by passing different
    commands and checking the output against expected values.
    """

    self.assertEqual(
        fire.Fire(tc.WithDefaults(), command=['double', '--count', '5']), 10)
    self.assertEqual(
        fire.Fire(tc.WithDefaults(), command=['triple', '--count', '5']), 15)

  def testFireDict(self):
    """Test the Fire function with a dictionary component.

    This function tests the Fire function by passing a dictionary component
    containing functions and values. It then asserts the output of the Fire
    function for different commands.

    Args:
        self: The object instance of the test case.
    """

    component = {
        'double': lambda x=0: 2 * x,
        'cheese': 'swiss',
    }
    self.assertEqual(fire.Fire(component, command=['double', '5']), 10)
    self.assertEqual(fire.Fire(component, command=['cheese']), 'swiss')

  def testFireObjectWithDict(self):
    """Test the behavior of the Fire object with dictionary input.

    This function tests the behavior of the Fire object with dictionary
    input by asserting the output for different commands and checking the
    instance type for certain commands.
    """

    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'echo']), 'E')
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'echo', 'lower']), 'e')
    self.assertIsInstance(
        fire.Fire(tc.TypedProperties, command=['delta', 'nest']), dict)
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'nest', '0']), 'a')

  def testFireSet(self):
    """Test the Fire function with a simple set component.

    This function creates a simple set component and tests the Fire function
    with an empty command list.
    """

    component = tc.simple_set()
    result = fire.Fire(component, command=[])
    self.assertEqual(len(result), 3)

  def testFireFrozenset(self):
    """Test the Fire function with a simple frozenset component.

    This function creates a simple frozenset component and tests the Fire
    function with an empty command list. It asserts that the length of the
    result is 3.
    """

    component = tc.simple_frozenset()
    result = fire.Fire(component, command=[])
    self.assertEqual(len(result), 3)

  def testFireList(self):
    """Test the Fire function with a list of components.

    This function tests the Fire function by passing a list of components
    and different commands to retrieve the expected output.

    Args:
        self: The object instance of the test case.
    """

    component = ['zero', 'one', 'two', 'three']
    self.assertEqual(fire.Fire(component, command=['2']), 'two')
    self.assertEqual(fire.Fire(component, command=['3']), 'three')
    self.assertEqual(fire.Fire(component, command=['-1']), 'three')

  def testFireObjectWithList(self):
    """Test the Fire object with a list command.

    This function tests the Fire object by passing a list command to it and
    checking the output.
    """

    self.assertEqual(fire.Fire(tc.TypedProperties, command=['echo', '0']),
                     'alex')
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['echo', '1']),
                     'bethany')

  def testFireObjectWithTuple(self):
    """Test the Fire object with a tuple command.

    This function tests the behavior of the Fire object when provided with a
    tuple command.

    Args:
        self: The test case object.
    """

    self.assertEqual(fire.Fire(tc.TypedProperties, command=['fox', '0']),
                     'carry')
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['fox', '1']),
                     'divide')

  def testFireObjectWithListAsObject(self):
    """Test the Fire object with a list as an object.

    This function tests the behavior of the Fire object when a list is
    passed as an object.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['echo', 'count', 'bethany']),
        1)

  def testFireObjectWithTupleAsObject(self):
    """Test the Fire object with a tuple as the object.

    This function tests the behavior of the Fire object when a tuple is
    passed as the object.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['fox', 'count', 'divide']),
        1)

  def testFireNoComponent(self):
    """Test the Fire function with no component specified.

    This function tests the Fire function by passing different commands and
    checking the output.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(fire.Fire(command=['tc', 'WithDefaults', 'double', '10']),
                     20)
    last_char = lambda text: text[-1]  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command=['last_char', '"Hello"']), 'o')
    self.assertEqual(fire.Fire(command=['last-char', '"World"']), 'd')
    rset = lambda count=0: set(range(count))  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command=['rset', '5']), {0, 1, 2, 3, 4})

  def testFireUnderscores(self):
    """Test the functionality of the Fire method with underscores in the
    command.

    This function tests the Fire method by passing commands with underscores
    to the Underscores class. It checks if the Fire method returns the
    expected output for the given commands.

    Args:
        self: The test case instance.
    """

    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore-example']), 'fish fingers')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_example']), 'fish fingers')

  def testFireUnderscoresInArg(self):
    """Test the functionality of Fire with underscores in arguments.

    This function tests the behavior of the Fire library when using
    underscores in arguments.

    Args:
        self: The instance of the test case.
    """

    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore-function', 'example']), 'example')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_function', '--underscore-arg=score']),
        'score')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_function', '--underscore_arg=score']),
        'score')

  def testBoolParsing(self):
    """Test the BoolConverter class by parsing boolean values.

    This function tests the BoolConverter class by parsing different boolean
    values and arguments.
    """

    self.assertEqual(fire.Fire(tc.BoolConverter, command=['as-bool', 'True']),
                     True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', 'False']), False)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--arg=True']), True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--arg=False']), False)
    self.assertEqual(fire.Fire(tc.BoolConverter, command=['as-bool', '--arg']),
                     True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--noarg']), False)

  def testBoolParsingContinued(self):
    """Test the parsing of boolean values in the command line arguments.

    This function tests the parsing of boolean values in the command line
    arguments using the Fire library.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', 'True', 'False']), (True, False))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha=False', '10']), (False, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta', '10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--noalpha', '--beta']), (False, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '10', '--beta']),
        (10, True))

  def testBoolParsingSingleHyphen(self):
    """Test the parsing of boolean values with single hyphen in command line
    arguments.

    This function tests the behavior of parsing boolean values with single
    hyphen in command line arguments.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha=False', '10']), (False, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-beta', '10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-noalpha', '-beta']), (False, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-10', '-beta']), (-10, True))

  def testBoolParsingLessExpectedCases(self):
    """Test various cases of boolean parsing with mixed defaults.

    This function tests different scenarios of boolean parsing with mixed
    defaults. It checks different combinations of input parameters and their
    expected outputs.
    """

    # Note: Does not return (True, 10).
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '10']), (10, '0'))
    # To get (True, 10), use one of the following:
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta=10']),
        (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', 'True', '10']), (True, 10))

    # Note: Does not return (True, '--test') or ('--test', 0).
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, command=['identity', '--alpha', '--test'])

    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--alpha', 'True', '"--test"']),
        (True, '--test'))
    # To get ('--test', '0'), use one of the following:
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['identity', '--alpha=--test']),
                     ('--test', '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=r'identity --alpha \"--test\"'),
        ('--test', '0'))

  def testSingleCharFlagParsing(self):
    """Test the parsing of single character flags in the Fire library.

    This function tests the parsing of single character flags in the Fire
    library by providing different command scenarios and asserting the
    expected outputs.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a']), (True, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '--beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '-b']), (True, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b']), (42, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b', '10']), (42, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', 'True', '-b', '10']),
        (True, 10))
    with self.assertRaisesFireExit(2):
      # This test attempts to use an ambiguous shortcut flag on a function with
      # a naming conflict for the shortcut, triggering a FireError.
      fire.Fire(tc.SimilarArgNames, command=['identity', '-b'])

  def testSingleCharFlagParsingEqualSign(self):
    """Test the parsing of single character flags with equal signs.

    This function tests the parsing of single character flags with equal
    signs in the command line arguments.

    Args:
        self: The object instance.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=True']), (True, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=3', '--beta=10']), (3, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=False', '-b=15']), (False, 15))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b=12']), (42, 12))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=42', '-b', '10']), (42, 10))

  def testSingleCharFlagParsingExactMatch(self):
    """Test the parsing of single character flags with exact matches.

    This function tests the parsing of single character flags with exact
    matches using the Fire library. It asserts the expected output for
    different command inputs.
    """

    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a']), (True, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a=10']), (10, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '--a']), (True, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-alpha']), (None, True))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a', '-alpha']), (True, True))

  def testSingleCharFlagParsingCapitalLetter(self):
    """Test the parsing of single character flags with capital letters.

    This function tests the parsing of single character flags with capital
    letters using the Fire library. It creates an instance of the
    CapitalizedArgNames class and calls the Fire function with the specified
    command to check if the expected result is returned.

    Returns:
        int: The sum of the values passed in the command.
    """

    self.assertEqual(
        fire.Fire(tc.CapitalizedArgNames,
                  command=['sum', '-D', '5', '-G', '10']), 15)

  def testBoolParsingWithNo(self):
    """Test boolean parsing with 'no' flag.

    This function tests the behavior of boolean parsing when using the 'no'
    flag. It includes various scenarios where the 'no' flag affects the
    boolean values passed to the function.
    """

    # In these examples --nothing always refers to the nothing argument:
    def fn1(thing, nothing):
      """Return the input 'thing' along with the 'nothing' argument.

      Args:
          thing: Any value to be returned.
          nothing: A placeholder argument with no specific functionality.

      Returns:
          tuple: A tuple containing the input 'thing' and the 'nothing' argument.
      """

      return thing, nothing

    self.assertEqual(fire.Fire(fn1, command=['--thing', '--nothing']),
                     (True, True))
    self.assertEqual(fire.Fire(fn1, command=['--thing', '--nonothing']),
                     (True, False))

    with self.assertRaisesFireExit(2):
      # In this case nothing=False (since rightmost setting of a flag gets
      # precedence), but it errors because thing has no value.
      fire.Fire(fn1, command=['--nothing', '--nonothing'])

    # In these examples, --nothing sets thing=False:
    def fn2(thing, **kwargs):
      """Return the input 'thing' along with any additional keyword arguments
      provided.

      Args:
          thing: Any value to be returned.
          **kwargs: Additional keyword arguments.

      Returns:
          tuple: A tuple containing 'thing' and any additional keyword arguments
              provided.
      """

      return thing, kwargs
    self.assertEqual(fire.Fire(fn2, command=['--thing']), (True, {}))
    self.assertEqual(fire.Fire(fn2, command=['--nothing']), (False, {}))
    with self.assertRaisesFireExit(2):
      # In this case, nothing=True, but it errors because thing has no value.
      fire.Fire(fn2, command=['--nothing=True'])
    self.assertEqual(fire.Fire(fn2, command=['--nothing', '--nothing=True']),
                     (False, {'nothing': True}))

    def fn3(arg, **kwargs):
      """Return the input argument and keyword arguments as a tuple.

      This function takes an argument and any additional keyword arguments and
      returns them as a tuple.

      Args:
          arg: Any value that is passed as the argument.
          **kwargs: Additional keyword arguments passed to the function.

      Returns:
          tuple: A tuple containing the input argument and keyword arguments.
      """

      return arg, kwargs
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--thing']),
                     ('value', {'thing': True}))
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--nothing']),
                     ('value', {'thing': False}))
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--nonothing']),
                     ('value', {'nothing': False}))

  def testTraceFlag(self):
    """Test the trace flag functionality in the Fire library.

    This function tests the behavior of the trace flag in the Fire library
    by calling Fire with different command line arguments.
    """

    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '--trace'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-t'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['--', '--trace'])

  def testHelpFlag(self):
    """Test the help flag functionality of the BoolConverter class.

    This function tests the behavior of the BoolConverter class when the
    help flag is provided as input.
    """

    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '--help'])
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-h'])
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['--', '--help'])

  def testHelpFlagAndTraceFlag(self):
    """Test the behavior of help flag and trace flag in the BoolConverter
    class.

    This function tests the behavior of help flag (--help, -h) and trace
    flag (--trace, -t) when passed as arguments to the BoolConverter class
    using the Fire library.
    """

    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter,
                command=['as-bool', 'True', '--', '--help', '--trace'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-h', '-t'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter, command=['--', '-h', '--trace'])

  def testTabCompletionNoName(self):
    """Test tab completion functionality without specifying a name.

    This function tests the tab completion functionality by creating a Fire
    instance with the specified command and checking if 'double' and
    'triple' are present in the completion script.

    Args:
        self: The test class instance.
    """

    completion_script = fire.Fire(tc.NoDefaults, command=['--', '--completion'])
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletion(self):
    """Test the tab completion functionality of the script.

    This function tests the tab completion feature of the script by
    simulating the tab key press and checking if the expected completions
    are present.
    """

    completion_script = fire.Fire(
        tc.NoDefaults, command=['--', '--completion'], name='c')
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletionWithDict(self):
    """Test tab completion functionality with a dictionary of actions.

    This function tests the tab completion feature using a dictionary of
    actions. It creates a dictionary with a 'multiply' action that
    multiplies two numbers. Then it generates a completion script using the
    Fire library with the provided actions. It checks if 'actCLI' and
    'multiply' are present in the completion script.

    Args:
        self: The test class instance.
    """

    actions = {'multiply': lambda a, b: a * b}
    completion_script = fire.Fire(
        actions, command=['--', '--completion'], name='actCLI')
    self.assertIn('actCLI', completion_script)
    self.assertIn('multiply', completion_script)

  def testBasicSeparator(self):
    """Test the basic functionality of the separator in the Fire module.

    This function tests the behavior of the separator in the Fire module by
    providing different commands and checking the expected output.
    """

    # '-' is the default separator.
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '+', '_']), ('+', '_'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '_', '+', '-']), ('_', '+'))

    # If we change the separator we can use '-' as an argument.
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-', '_', '--', '--separator', '&']),
        ('-', '_'))

    # The separator triggers a function call, but there aren't enough arguments.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, command=['identity', '-', '_', '+'])

  def testNonComparable(self):
    """    Fire should work with classes that disallow comparisons.

    This function tests the behavior of the Fire module when working with
    classes that disallow comparisons. It checks if the Fire module can
    instantiate the NonComparable object using different types of commands.
    """
    # Make sure this test passes both with a string command or a list command.
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=''), tc.NonComparable)
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=[]), tc.NonComparable)

    # The first separator instantiates the NonComparable object.
    # The second separator causes Fire to check if the separator was necessary.
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=['-', '-']), tc.NonComparable)

  def testExtraSeparators(self):
    """Test the behavior of the Fire function with extra separators in the
    command list.

    This function tests the behavior of the Fire function when extra
    separators are present in the command list.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', '-', 'as-bool', 'True']),
        True)
    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', '-', '-', 'as-bool',
                     'True']),
        True)

  def testSeparatorForChaining(self):
    """Test the behavior of separator for chaining in the Fire module.

    This function tests the behavior of the separator for chaining in the
    Fire module. It checks how different separators affect the arguments
    consumed by the get_obj function.

    Args:
        self: The instance of the test class.
    """

    # Without a separator all args are consumed by get_obj.
    self.assertIsInstance(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', 'arg2', 'as-bool', 'True']),
        tc.BoolConverter)
    # With a separator only the preceding args are consumed by get_obj.
    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', 'as-bool', 'True']), True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', 'arg2', '&', 'as-bool', 'True',
                           '--', '--separator', '&']),
        True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', '$$', 'as-bool', 'True', '--',
                           '--separator', '$$']),
        True)

  def testNegativeNumbers(self):
    """Test the functionality of the 'MixedDefaults' class with negative
    numbers.

    This test case checks if the 'sum' command of the 'MixedDefaults' class
    correctly calculates the sum of negative numbers provided as input
    arguments.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '-3', '--beta', '-4']), -11)

  def testFloatForExpectedInt(self):
    """Test the conversion of float inputs to expected integer outputs.

    This function tests the behavior of converting float inputs to expected
    integer outputs using the Fire library.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '2.2', '--beta', '3.0']), 8.2)
    self.assertEqual(
        fire.Fire(
            tc.NumberDefaults,
            command=['integer_reciprocal', '--divisor', '5.0']), 0.2)
    self.assertEqual(
        fire.Fire(tc.NumberDefaults, command=['integer_reciprocal', '4.0']),
        0.25)

  def testClassInstantiation(self):
    """Test the instantiation of a class using Fire library.

    This function tests the instantiation of a class using the Fire library.
    It checks if the class instance is of the expected type and if an
    exception is raised when trying to instantiate the class with positional
    arguments.

    Args:
        self: The test case instance.
    """

    self.assertIsInstance(fire.Fire(tc.InstanceVars,
                                    command=['--arg1=a1', '--arg2=a2']),
                          tc.InstanceVars)
    with self.assertRaisesFireExit(2):
      # Cannot instantiate a class with positional args.
      fire.Fire(tc.InstanceVars, command=['a1', 'a2'])

  def testTraceErrors(self):
    """Test various error scenarios in the testTraceErrors function.

    This function tests different error scenarios by calling the fire.Fire
    method with different command arguments. It checks for cases where
    additional values are needed but run out of arguments, extra args cannot
    be consumed, and when a member to access cannot be found.
    """

    # Class needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['--arg1=a1'])

    # Routine needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1', 'a2', '-', 'run', 'b1'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars,
                command=['--arg1=a1', '--arg2=a2', '-', 'run b1'])

    # Extra args cannot be consumed.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars,
                command=['a1', 'a2', '-', 'run', 'b1', 'b2', 'b3'])
    with self.assertRaisesFireExit(2):
      fire.Fire(
          tc.InstanceVars,
          command=['--arg1=a1', '--arg2=a2', '-', 'run', 'b1', 'b2', 'b3'])

    # Cannot find member to access.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1', 'a2', '-', 'jog'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['--arg1=a1', '--arg2=a2', '-', 'jog'])

  def testClassWithDefaultMethod(self):
    """Test the DefaultMethod class with the 'double' command and input number.

    This function tests the DefaultMethod class by passing the 'double'
    command along with an input number. It asserts that the output value is
    equal to 20.

    Args:
        self: The test class instance.
    """

    self.assertEqual(
        fire.Fire(tc.DefaultMethod, command=['double', '10']), 20
    )

  def testClassWithInvalidProperty(self):
    """Test the functionality of the InvalidProperty class with the given
    command.

    Args:
        self: The test class instance.
    """

    self.assertEqual(
        fire.Fire(tc.InvalidProperty, command=['double', '10']), 20
    )

  @testutils.skipIf(sys.version_info[0:2] <= (3, 4),
                    'Cannot inspect wrapped signatures in Python 2 or 3.4.')
  def testHelpKwargsDecorator(self):
    """Test the behavior of the help flag when using a decorator.

    This function tests the behavior of the help flag when using a decorator
    by simulating calling the decorated method with the help flag as a
    command. It checks if the function does not crash and exits with code 0
    when the help flag is provided.
    """

    # Issue #190, follow the wrapped method instead of crashing.
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.decorated_method, command=['-h'])
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.decorated_method, command=['--help'])

  @testutils.skipIf(six.PY2, 'Asyncio not available in Python 2.')
  def testFireAsyncio(self):
    """Test the FireAsyncio function.

    This function tests the FireAsyncio function by asserting that the
    result of calling Fire with WithAsyncio class and specific command
    arguments is equal to 20.

    Args:
        self: The test case object.
    """

    self.assertEqual(fire.Fire(tc.py3.WithAsyncio,
                               command=['double', '--count', '10']), 20)


if __name__ == '__main__':
  testutils.main()
