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

"""Tests for the parser module."""

from fire import parser
from fire import testutils


class ParserTest(testutils.BaseTestCase):

  def testCreateParser(self):
    """Test the CreateParser function for not returning None.

    This function tests the CreateParser function to ensure that it does not
    return None.
    """

    self.assertIsNotNone(parser.CreateParser())

  def testSeparateFlagArgs(self):
    """Test the SeparateFlagArgs function in the parser module.

    This function tests the behavior of SeparateFlagArgs function with
    different input scenarios.

    Args:
        self: The object instance of the test case.
    """

    self.assertEqual(parser.SeparateFlagArgs([]), ([], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b']), (['a', 'b'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--']),
                     (['a', 'b'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c']),
                     (['a', 'b'], ['c']))
    self.assertEqual(parser.SeparateFlagArgs(['--']),
                     ([], []))
    self.assertEqual(parser.SeparateFlagArgs(['--', 'c', 'd']),
                     ([], ['c', 'd']))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', 'd']),
                     (['a', 'b'], ['c', 'd']))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', 'd', '--']),
                     (['a', 'b', '--', 'c', 'd'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', '--', 'd']),
                     (['a', 'b', '--', 'c'], ['d']))

  def testDefaultParseValueStrings(self):
    """Test the DefaultParseValue function with various input strings.

    This function tests the DefaultParseValue function with different input
    strings to ensure it returns the correct output.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue('hello'), 'hello')
    self.assertEqual(parser.DefaultParseValue('path/file.jpg'), 'path/file.jpg')
    self.assertEqual(parser.DefaultParseValue('hello world'), 'hello world')
    self.assertEqual(parser.DefaultParseValue('--flag'), '--flag')

  def testDefaultParseValueQuotedStrings(self):
    """Test the DefaultParseValue function with quoted strings.

    This function tests the DefaultParseValue function with various quoted
    strings to ensure that it correctly parses and returns the unquoted
    string.
    """

    self.assertEqual(parser.DefaultParseValue("'hello'"), 'hello')
    self.assertEqual(parser.DefaultParseValue("'hello world'"), 'hello world')
    self.assertEqual(parser.DefaultParseValue("'--flag'"), '--flag')
    self.assertEqual(parser.DefaultParseValue('"hello"'), 'hello')
    self.assertEqual(parser.DefaultParseValue('"hello world"'), 'hello world')
    self.assertEqual(parser.DefaultParseValue('"--flag"'), '--flag')

  def testDefaultParseValueSpecialStrings(self):
    """Test the DefaultParseValue function with special strings.

    This function tests the behavior of the DefaultParseValue function when
    provided with special strings such as '-', '--', '---', '----', 'None',
    and "'None'".
    """

    self.assertEqual(parser.DefaultParseValue('-'), '-')
    self.assertEqual(parser.DefaultParseValue('--'), '--')
    self.assertEqual(parser.DefaultParseValue('---'), '---')
    self.assertEqual(parser.DefaultParseValue('----'), '----')
    self.assertEqual(parser.DefaultParseValue('None'), None)
    self.assertEqual(parser.DefaultParseValue("'None'"), 'None')

  def testDefaultParseValueNumbers(self):
    """Test the DefaultParseValue function with various input values.

    This function tests the DefaultParseValue function by passing different
    string representations of numbers and checking if the function correctly
    converts them to their respective numeric values.

    Args:
        self: The test case instance.
    """

    self.assertEqual(parser.DefaultParseValue('23'), 23)
    self.assertEqual(parser.DefaultParseValue('-23'), -23)
    self.assertEqual(parser.DefaultParseValue('23.0'), 23.0)
    self.assertIsInstance(parser.DefaultParseValue('23'), int)
    self.assertIsInstance(parser.DefaultParseValue('23.0'), float)
    self.assertEqual(parser.DefaultParseValue('23.5'), 23.5)
    self.assertEqual(parser.DefaultParseValue('-23.5'), -23.5)

  def testDefaultParseValueStringNumbers(self):
    """Test the DefaultParseValue function with string input containing
    numbers.

    This function tests the DefaultParseValue function by passing string
    inputs containing numbers in different formats such as integers and
    floats. It checks if the function correctly parses and returns the
    numeric values as strings.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue("'23'"), '23')
    self.assertEqual(parser.DefaultParseValue("'23.0'"), '23.0')
    self.assertEqual(parser.DefaultParseValue("'23.5'"), '23.5')
    self.assertEqual(parser.DefaultParseValue('"23"'), '23')
    self.assertEqual(parser.DefaultParseValue('"23.0"'), '23.0')
    self.assertEqual(parser.DefaultParseValue('"23.5"'), '23.5')

  def testDefaultParseValueQuotedStringNumbers(self):
    """Test the DefaultParseValue function with a quoted string input
    containing numbers.

    This function tests the DefaultParseValue function by passing a quoted
    string input containing numbers. It asserts that the output is the same
    as the input without the quotes.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue('"\'123\'"'), "'123'")

  def testDefaultParseValueOtherNumbers(self):
    """Test the DefaultParseValue function with a scientific notation number.

    This test case checks if the DefaultParseValue function correctly parses
    a scientific notation number and returns the corresponding float value.

    Args:
        self: Instance of the test class.
    """

    self.assertEqual(parser.DefaultParseValue('1e5'), 100000.0)

  def testDefaultParseValueLists(self):
    """Test the DefaultParseValue function with lists as input.

    This function tests the DefaultParseValue function by passing lists with
    different types of elements as input.
    """

    self.assertEqual(parser.DefaultParseValue('[1, 2, 3]'), [1, 2, 3])
    self.assertEqual(parser.DefaultParseValue('[1, "2", 3]'), [1, '2', 3])
    self.assertEqual(parser.DefaultParseValue('[1, \'"2"\', 3]'), [1, '"2"', 3])
    self.assertEqual(parser.DefaultParseValue(
        '[1, "hello", 3]'), [1, 'hello', 3])

  def testDefaultParseValueBareWordsLists(self):
    """Test the DefaultParseValue function with a string containing bare words
    and lists.

    This function tests the DefaultParseValue function by passing a string
    that contains bare words and lists. It checks if the function correctly
    parses the input string and returns a list with the elements.

    Returns:
        list: A list containing the parsed elements from the input string.
    """

    self.assertEqual(parser.DefaultParseValue('[one, 2, "3"]'), ['one', 2, '3'])

  def testDefaultParseValueDict(self):
    """Test the DefaultParseValue function with a dictionary input.

    This function tests the DefaultParseValue function by passing a
    dictionary input and checking if the output matches the expected
    dictionary.

    Returns:
        dict: The parsed dictionary from the input string.
    """

    self.assertEqual(
        parser.DefaultParseValue('{"abc": 5, "123": 1}'), {'abc': 5, '123': 1})

  def testDefaultParseValueNone(self):
    """Test the DefaultParseValue function with input 'None'.

    This function tests the DefaultParseValue function by passing 'None' as
    input and checking if the output is None.

    Args:
        self: The object itself.
    """

    self.assertEqual(parser.DefaultParseValue('None'), None)

  def testDefaultParseValueBool(self):
    """Test the DefaultParseValue function for boolean values.

    This function tests the DefaultParseValue function to ensure that it
    correctly parses the input strings 'True' and 'False' to their
    corresponding boolean values.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue('True'), True)
    self.assertEqual(parser.DefaultParseValue('False'), False)

  def testDefaultParseValueBareWordsTuple(self):
    """Test the DefaultParseValue function with input containing bare words
    tuple.

    This function tests the DefaultParseValue function by passing input
    strings containing bare words tuple. It asserts that the function
    correctly parses the input and returns a tuple of values.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue('(one, 2, "3")'), ('one', 2, '3'))
    self.assertEqual(parser.DefaultParseValue('one, "2", 3'), ('one', '2', 3))

  def testDefaultParseValueNestedContainers(self):
    """Test the DefaultParseValue function with nested containers.

    This function tests the DefaultParseValue function by passing a string
    representation of nested containers and checking if the function
    correctly parses and returns the nested containers.

    Args:
        self: The test case object.
    """

    self.assertEqual(
        parser.DefaultParseValue(
            '[(A, 2, "3"), 5, {alpha: 10.2, beta: "cat"}]'),
        [('A', 2, '3'), 5, {'alpha': 10.2, 'beta': 'cat'}])

  def testDefaultParseValueComments(self):
    """Test the DefaultParseValue function with comments.

    This function tests the DefaultParseValue function with comments
    included in the input string. It checks if the function correctly
    handles the input string with comments and returns the expected output.

    Args:
        self: The test case object.
    """

    self.assertEqual(parser.DefaultParseValue('"0#comments"'), '0#comments')
    # Comments are stripped. This behavior may change in the future.
    self.assertEqual(parser.DefaultParseValue('0#comments'), 0)

  def testDefaultParseValueBadLiteral(self):
    """Test the DefaultParseValue function when the input value cannot be
    parsed correctly.

    This function tests the behavior of DefaultParseValue when the input
    value cannot be parsed correctly, and it treats it as a string. The
    behavior of treating unparsable values as strings may change in the
    future.

    Args:
        self: The instance of the test case.
    """

    # If it can't be parsed, we treat it as a string. This behavior may change.
    self.assertEqual(
        parser.DefaultParseValue('[(A, 2, "3"), 5'), '[(A, 2, "3"), 5')
    self.assertEqual(parser.DefaultParseValue('x=10'), 'x=10')

  def testDefaultParseValueSyntaxError(self):
    """Test the default parse value function when the input cannot be parsed.

    This function tests the behavior of the default parse value function
    when the input value cannot be parsed and ensures that it returns the
    input value as a string.

    Args:
        self: The object instance of the test case.
    """

    # If it can't be parsed, we treat it as a string.
    self.assertEqual(parser.DefaultParseValue('"'), '"')

  def testDefaultParseValueIgnoreBinOp(self):
    """Test the DefaultParseValue function with input values that are not
    binary operations.

    This function tests the DefaultParseValue function by passing in input
    values that are not binary operations. It checks if the function returns
    the same value as the input.

    Args:
        self: The object instance of the test case.
    """

    self.assertEqual(parser.DefaultParseValue('2017-10-10'), '2017-10-10')
    self.assertEqual(parser.DefaultParseValue('1+1'), '1+1')

if __name__ == '__main__':
  testutils.main()
