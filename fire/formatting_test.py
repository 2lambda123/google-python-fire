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

"""Tests for formatting.py."""

from fire import formatting
from fire import testutils

LINE_LENGTH = 80


class FormattingTest(testutils.BaseTestCase):

  def test_bold(self):
    """Test the Bold formatting function.

    This function tests the Bold formatting function by creating a Bold
    object with the input text and checking if the output is as expected.

    Args:
        self: The object itself.
    """

    text = formatting.Bold('hello')
    self.assertIn(text, ['hello', '\x1b[1mhello\x1b[0m'])

  def test_underline(self):
    """Test the Underline class in the formatting module.

    This function creates an instance of the Underline class with the input
    text 'hello' and checks if the output text is either 'hello' or
    '\x1b[4mhello\x1b[0m'.

    Args:
        self: The instance of the test case.
    """

    text = formatting.Underline('hello')
    self.assertIn(text, ['hello', '\x1b[4mhello\x1b[0m'])

  def test_indent(self):
    """Test the Indent class from the formatting module.

    This function creates an instance of the Indent class with the input
    text and specified number of spaces. It then checks if the output text
    has the correct indentation.

    Args:
        self: The object instance.
    """

    text = formatting.Indent('hello', spaces=2)
    self.assertEqual('  hello', text)

  def test_indent_multiple_lines(self):
    """Test the Indent function of the formatting module.

    This function tests the Indent function of the formatting module by
    creating an Indent object with the input text and specified number of
    spaces for indentation.

    Args:
        self: The object instance.
    """

    text = formatting.Indent('hello\nworld', spaces=2)
    self.assertEqual('  hello\n  world', text)

  def test_wrap_one_item(self):
    """Test the WrappedJoin class with a single item.

    This function creates an instance of the WrappedJoin class with a list
    containing a single item. It then asserts that the output of the
    WrappedJoin class is equal to the input list.

    Args:
        self: The instance of the test case.
    """

    lines = formatting.WrappedJoin(['rice'])
    self.assertEqual(['rice'], lines)

  def test_wrap_multiple_items(self):
    """Test the WrappedJoin function with multiple items to be wrapped within a
    specified width.

    This function tests the behavior of the WrappedJoin function when
    provided with a list of multiple items and a specified width for
    wrapping.

    Args:
        self: The object instance of the test case.
    """

    lines = formatting.WrappedJoin(['rice', 'beans', 'chicken', 'cheese'],
                                   width=15)
    self.assertEqual(['rice | beans |',
                      'chicken |',
                      'cheese'], lines)

  def test_ellipsis_truncate(self):
    """Test the EllipsisTruncate function to truncate a text string with an
    ellipsis.

    This function tests the EllipsisTruncate function by providing a text
    string and checking if it is correctly truncated with an ellipsis based
    on the available space and line length.

    Args:
        self: The test case object.
    """

    text = 'This is a string'
    truncated_text = formatting.EllipsisTruncate(
        text=text, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual('This is...', truncated_text)

  def test_ellipsis_truncate_not_enough_space(self):
    """Test the EllipsisTruncate function when there is not enough space to
    truncate.

    This function tests the behavior of the EllipsisTruncate function when
    the available space is not enough to truncate the text. It checks if the
    original text remains unchanged in this scenario.

    Args:
        self: The test case object.
    """

    text = 'This is a string'
    truncated_text = formatting.EllipsisTruncate(
        text=text, available_space=2, line_length=LINE_LENGTH)
    self.assertEqual('This is a string', truncated_text)

  def test_ellipsis_middle_truncate(self):
    """Test the EllipsisMiddleTruncate function with the given text and
    available space.

    This function tests the EllipsisMiddleTruncate function by passing a
    text and available space to check if the text is truncated correctly
    from the middle.

    Args:
        text (str): The input text to be truncated.
        available_space (int): The available space for the truncated text.
        line_length (int): The length of the line.

    Returns:
        str: The truncated text with ellipsis in the middle.
    """

    text = '1000000000L'
    truncated_text = formatting.EllipsisMiddleTruncate(
        text=text, available_space=7, line_length=LINE_LENGTH)
    self.assertEqual('10...0L', truncated_text)

  def test_ellipsis_middle_truncate_not_enough_space(self):
    """Test the EllipsisMiddleTruncate function when there is not enough space
    for truncation.

    This test case checks the behavior of the EllipsisMiddleTruncate
    function when the available space for truncation is less than the length
    of the text. It verifies that the original text remains unchanged in
    this scenario.

    Args:
        self: The test case object.
    """

    text = '1000000000L'
    truncated_text = formatting.EllipsisMiddleTruncate(
        text=text, available_space=2, line_length=LINE_LENGTH)
    self.assertEqual('1000000000L', truncated_text)


if __name__ == '__main__':
  testutils.main()
