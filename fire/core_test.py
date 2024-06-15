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

"""Tests for the core module."""

from fire import core
from fire import test_components as tc
from fire import testutils
from fire import trace
import mock

import six


class CoreTest(testutils.BaseTestCase):

  def testOneLineResult(self):
    """Test the _OneLineResult function.

    This function tests the _OneLineResult function by passing different
    types of input values and checking if the function returns the expected
    output.

    Args:
        self: The object instance.
    """

    self.assertEqual(core._OneLineResult(1), '1')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult('hello'), 'hello')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult({}), '{}')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult({'x': 'y'}), '{"x": "y"}')  # pylint: disable=protected-access

  def testOneLineResultCircularRef(self):
    """Test the _OneLineResult function with CircularReference object.

    This function creates a CircularReference object and tests the
    _OneLineResult function by passing the result of
    circular_reference.create() as input. It asserts that the output is
    equal to "{'y': {...}}".

    Args:
        self: The test case object.
    """

    circular_reference = tc.CircularReference()
    self.assertEqual(core._OneLineResult(circular_reference.create()),  # pylint: disable=protected-access
                     "{'y': {...}}")

  @mock.patch('fire.interact.Embed')
  def testInteractiveMode(self, mock_embed):
    """Test the interactive mode functionality of the Fire command line
    interface.

    This function tests the behavior of the Fire command line interface when
    the interactive mode flag is used.

    Args:
        mock_embed: Mock object for embed functionality.
    """

    core.Fire(tc.TypedProperties, command=['alpha'])
    self.assertFalse(mock_embed.called)
    core.Fire(tc.TypedProperties, command=['alpha', '--', '-i'])
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeFullArgument(self, mock_embed):
    """Test the interactive mode with full argument.

    This function tests the interactive mode by calling Fire with specific
    arguments and asserts that the mock_embed function is called.

    Args:
        self: The test class instance.
        mock_embed: Mock object for the embed function.
    """

    core.Fire(tc.TypedProperties, command=['alpha', '--', '--interactive'])
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariables(self, mock_embed):
    """Test the interactive mode variables in the Fire command.

    This function tests the interactive mode variables by calling the Fire
    command with specific arguments and then asserting various conditions on
    the output.

    Args:
        self: The instance of the test class.
        mock_embed: The mock object for embedding.
    """

    core.Fire(tc.WithDefaults, command=['double', '2', '--', '-i'])
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertFalse(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariablesWithName(self, mock_embed):
    """Test the interactive mode variables with a specific name.

    This function tests the behavior of interactive mode variables when a
    specific name is provided. It calls the Fire method with specific
    arguments and asserts various conditions on the variables.

    Args:
        mock_embed: Mock object for embed.
    """

    core.Fire(tc.WithDefaults,
              command=['double', '2', '--', '-i', '-v'], name='D')
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertTrue(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertEqual(variables['D'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  # TODO(dbieber): Use parameterized tests to break up repetitive tests.
  def testHelpWithClass(self):
    """Test the help functionality of a class using Fire.

    This function tests the help functionality of a class using Fire by
    checking if the expected output is generated when providing different
    command line arguments.
    """

    with self.assertRaisesFireExit(0, 'SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['-h'])

  def testHelpWithMember(self):
    """Test the help message for different commands using FireExit.

    This function tests the help message for different commands using
    FireExit. It asserts that the help message contains specific information
    for each command.
    """

    with self.assertRaisesFireExit(0, 'SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '-h'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*delta'):
      core.Fire(tc.TypedProperties, command=['delta', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*echo'):
      core.Fire(tc.TypedProperties, command=['echo', '--help'])

  def testHelpOnErrorInConstructor(self):
    """Test the behavior of FireExit and FireExitNotRaised exceptions in
    ErrorInConstructor.

    This function tests the behavior of the ErrorInConstructor class when
    FireExit and FireExitNotRaised exceptions are raised. It checks if the
    correct exit code and message are displayed when the exceptions are
    raised.
    """

    with self.assertRaisesFireExit(0, 'SYNOPSIS.*VALUE'):
      core.Fire(tc.ErrorInConstructor, command=['--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*VALUE'):
      core.Fire(tc.ErrorInConstructor, command=['--help'])

  def testHelpWithNamespaceCollision(self):
    """Test cases for handling namespace collision when calling the help
    shortcut.

    This function tests different scenarios where calling the help shortcut
    should not display help messages.

    Args:
        self: The test class instance.
    """

    # Tests cases when calling the help shortcut should not show help.
    with self.assertOutputMatches(stdout='DESCRIPTION.*', stderr=None):
      core.Fire(tc.WithHelpArg, command=['--help', 'False'])
    with self.assertOutputMatches(stdout='help in a dict', stderr=None):
      core.Fire(tc.WithHelpArg, command=['dictionary', '__help'])
    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.WithHelpArg, command=['dictionary', '--help'])
    with self.assertOutputMatches(stdout='False', stderr=None):
      core.Fire(tc.function_with_help, command=['False'])

  def testInvalidParameterRaisesFireExit(self):
    """Test that FireExit is raised when an invalid parameter is provided.

    This test checks if FireExit exception is raised when an invalid
    parameter is provided to the Fire command.
    """

    with self.assertRaisesFireExit(2, 'runmisspelled'):
      core.Fire(tc.Kwargs, command=['props', '--a=1', '--b=2', 'runmisspelled'])

  def testErrorRaising(self):
    """Test that errors in user code are not caught and surface as normal.

    This test ensures that errors raised in user code are not caught but
    instead surface as normal, leading to an exit status code of 1 for the
    client program.
    """

    # Errors in user code should not be caught; they should surface as normal.
    # This will lead to exit status code 1 for the client program.
    with self.assertRaises(ValueError):
      core.Fire(tc.ErrorRaiser, command=['fail'])

  def testFireError(self):
    """Test the creation of a FireError instance.

    This function creates a FireError instance with the given error message.

    Args:
        self: The test case object.
    """

    error = core.FireError('Example error')
    self.assertIsNotNone(error)

  def testFireErrorMultipleValues(self):
    """Test the creation of a FireError instance with multiple values.

    This function creates a FireError instance with the provided error
    message and value.

    Args:
        self: The instance of the test case.
    """

    error = core.FireError('Example error', 'value')
    self.assertIsNotNone(error)

  def testPrintEmptyDict(self):
    """Test the printing of an empty dictionary.

    This function tests the behavior of printing an empty dictionary using
    the core module's Fire method.

    Args:
        self: The test case object.
    """

    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.EmptyDictOutput, command=['totally_empty'])
    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.EmptyDictOutput, command=['nothing_printable'])

  def testPrintOrderedDict(self):
    """Test the printing of an ordered dictionary.

    This function tests the printing of an ordered dictionary by checking
    the output when the dictionary is non-empty and when it is empty.

    Args:
        self: The test case object.
    """

    with self.assertOutputMatches(stdout=r'A:\s+A\s+2:\s+2\s+', stderr=None):
      core.Fire(tc.OrderedDictionary, command=['non_empty'])
    with self.assertOutputMatches(stdout='{}'):
      core.Fire(tc.OrderedDictionary, command=['empty'])

  def testPrintNamedTupleField(self):
    """Test the printing of a named tuple field.

    This function tests the functionality of printing a specific field of a
    named tuple.
    """

    with self.assertOutputMatches(stdout='11', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', 'x'])

  def testPrintNamedTupleFieldNameEqualsValue(self):
    """Test the functionality of printing a named tuple field name that equals
    a specific value.

    This function tests the behavior of the 'Fire' method from the 'core'
    module when provided with a NamedTuple instance and a specific command.
    It asserts that the output matches the expected standard output value
    'x' and that there is no standard error output.
    """

    with self.assertOutputMatches(stdout='x', stderr=None):
      core.Fire(tc.NamedTuple, command=['matching_names', 'x'])

  def testPrintNamedTupleIndex(self):
    """Test the functionality of printing a named tuple index.

    This function tests the behavior of printing a specific index of a named
    tuple.

    Args:
        self: The test case instance.
    """

    with self.assertOutputMatches(stdout='22', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', '1'])

  def testPrintSet(self):
    """Test the printing of a set by checking the output matches the expected
    string 'three'.

    This function tests the printing of a set by using assertOutputMatches
    to check if the output matches the expected string 'three' when calling
    core.Fire with a simple_set and empty command list.

    Args:
        self: The test case instance.
    """

    with self.assertOutputMatches(stdout='.*three.*', stderr=None):
      core.Fire(tc.simple_set(), command=[])

  def testPrintFrozenSet(self):
    """Test the functionality of printing a frozen set.

    This function tests the ability to print a frozen set by asserting that
    the output matches the string 'three' in the standard output.
    """

    with self.assertOutputMatches(stdout='.*three.*', stderr=None):
      core.Fire(tc.simple_frozenset(), command=[])

  def testPrintNamedTupleNegativeIndex(self):
    """Test the functionality of printing a named tuple with a negative index.

    This function tests the behavior of printing a named tuple with a
    negative index by using the Fire command with the specified arguments.
    """

    with self.assertOutputMatches(stdout='11', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', '-2'])

  def testCallable(self):
    """Test the callable function with different command inputs.

    This function tests the behavior of the callable function with different
    command inputs. It uses assertOutputMatches to check the stdout output
    for different scenarios.

    Args:
        self: The instance of the test class.
    """

    with self.assertOutputMatches(stdout=r'foo:\s+foo\s+', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=['--foo=foo'])
    with self.assertOutputMatches(stdout=r'foo\s+', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=['print_msg', 'foo'])
    with self.assertOutputMatches(stdout=r'', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=[])

  def testCallableWithPositionalArgs(self):
    """Test the behavior of a callable object with positional arguments.

    This test checks the behavior of a callable object when positional
    arguments are provided. It verifies that an expected FireExit exception
    is raised when positional arguments are used.

    Args:
        self: The test instance.
    """

    with self.assertRaisesFireExit(2, ''):
      # This does not give 7 since positional args are disallowed for callable
      # objects.
      core.Fire(tc.CallableWithPositionalArgs(), command=['3', '4'])

  def testStaticMethod(self):
    """Test the static method functionality of the Fire class.

    This method tests the functionality of the static method in the Fire
    class by calling the Fire function with specific arguments and asserting
    that the output matches the expected value.

    Returns:
        str: The expected output value from the static method call.
    """

    self.assertEqual(
        core.Fire(tc.HasStaticAndClassMethods,
                  command=['static_fn', 'alpha']),
        'alpha',
    )

  def testClassMethod(self):
    """Test the class method 'HasStaticAndClassMethods.class_fn' with input
    arguments.

    This method tests the class method 'HasStaticAndClassMethods.class_fn'
    by passing the input arguments 'class_fn' and '6' to the Fire function
    from the core module and asserts that the returned value is 7.

    Args:
        self: The object instance of the test case.
    """

    self.assertEqual(
        core.Fire(tc.HasStaticAndClassMethods,
                  command=['class_fn', '6']),
        7,
    )

  def testCustomSerialize(self):
    """Test the custom serialization function.

    This function tests the custom serialization logic by passing different
    types of input values and checking the output after serialization.

    Args:
        self: The instance of the test class.
    """

    def serialize(x):
      """Serialize the input data into a string representation.

      This function takes an input data and serializes it into a string
      representation based on the type of the input. If the input is a list,
      it joins the elements with ', '. If the input is a dictionary, it joins
      the key-value pairs with ', '. If the input is 'special', it returns a
      predefined list. Otherwise, it returns the input as is.

      Args:
          x: Input data to be serialized.

      Returns:
          str or list or any: A string representation of the input data based on
              its type.
      """

      if isinstance(x, list):
        return ', '.join(str(xi) for xi in x)
      if isinstance(x, dict):
        return ', '.join('{}={!r}'.format(k, v) for k, v in sorted(x.items()))
      if x == 'special':
        return ['SURPRISE!!', "I'm a list!"]
      return x

    ident = lambda x: x

    with self.assertOutputMatches(stdout='a, b', stderr=None):
      _ = core.Fire(ident, command=['[a,b]'], serialize=serialize)
    with self.assertOutputMatches(stdout='a=5, b=6', stderr=None):
      _ = core.Fire(ident, command=['{a:5,b:6}'], serialize=serialize)
    with self.assertOutputMatches(stdout='asdf', stderr=None):
      _ = core.Fire(ident, command=['asdf'], serialize=serialize)
    with self.assertOutputMatches(
        stdout="SURPRISE!!\nI'm a list!\n", stderr=None):
      _ = core.Fire(ident, command=['special'], serialize=serialize)
    with self.assertRaises(core.FireError):
      core.Fire(ident, command=['asdf'], serialize=55)

  @testutils.skipIf(six.PY2, 'lru_cache is Python 3 only.')
  def testLruCacheDecoratorBoundArg(self):
    """Test the LRU cache decorator with bound argument.

    This function tests the LRU cache decorator with a bound argument by
    asserting the result of calling the core.Fire method with specified
    arguments.

    Args:
        self: The instance of the test class.
    """

    self.assertEqual(
        core.Fire(tc.py3.LruCacheDecoratedMethod,  # pytype: disable=module-attr
                  command=['lru_cache_in_class', 'foo']), 'foo')

  @testutils.skipIf(six.PY2, 'lru_cache is Python 3 only.')
  def testLruCacheDecorator(self):
    """Test the LRU cache decorator functionality.

    This function tests the LRU cache decorator by calling the decorated
    function with a specific command and asserting the result.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        core.Fire(tc.py3.lru_cache_decorated,  # pytype: disable=module-attr
                  command=['foo']), 'foo')


if __name__ == '__main__':
  testutils.main()
