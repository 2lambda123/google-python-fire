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

"""Formatting utilities for use in creating help text."""

from fire import formatting_windows  # pylint: disable=unused-import
import termcolor


ELLIPSIS = '...'


def Indent(text, spaces=2):
  """Indent each line of the input text by the specified number of spaces.

  Args:
      text (str): The input text to be indented.
      spaces (int): The number of spaces to indent each line by (default is 2).

  Returns:
      str: The indented text.
  """

  lines = text.split('\n')
  return '\n'.join(
      ' ' * spaces + line if line else line
      for line in lines)


def Bold(text):
  """Make the text bold using termcolor.

  Args:
      text (str): The text to be made bold.

  Returns:
      str: The input text formatted in bold.
  """

  return termcolor.colored(text, attrs=['bold'])


def Underline(text):
  """Underline the given text using termcolor.

  Args:
      text (str): The text to be underlined.

  Returns:
      str: The underlined text.
  """

  return termcolor.colored(text, attrs=['underline'])


def BoldUnderline(text):
  """Apply bold and underline formatting to the input text.

  Args:
      text (str): The text to be formatted.

  Returns:
      str: The formatted text with both bold and underline styles.
  """

  return Bold(Underline(text))


def WrappedJoin(items, separator=' | ', width=80):
  """  Joins the items by the separator, wrapping lines at the given width.

  Args:
      items (list): A list of strings to be joined.
      separator (str?): The separator to use between items. Defaults to ' | '.
      width (int?): The maximum width at which to wrap lines. Defaults to 80.

  Returns:
      list: A list of strings where items are joined with the separator and lines
          are wrapped at the specified width.
  """
  lines = []
  current_line = ''
  for index, item in enumerate(items):
    is_final_item = index == len(items) - 1
    if is_final_item:
      if len(current_line) + len(item) <= width:
        current_line += item
      else:
        lines.append(current_line.rstrip())
        current_line = item
    else:
      if len(current_line) + len(item) + len(separator) <= width:
        current_line += item + separator
      else:
        lines.append(current_line.rstrip())
        current_line = item + separator

  lines.append(current_line)
  return lines


def Error(text):
  """Return the input text formatted as a red colored and bold string.

  Args:
      text (str): The input text to be formatted.

  Returns:
      str: The formatted text with red color and bold attributes.
  """

  return termcolor.colored(text, color='red', attrs=['bold'])


def EllipsisTruncate(text, available_space, line_length):
  """  Truncate text from the end with ellipsis.

  This function truncates the input text from the end with an ellipsis if
  the length of the text exceeds the available space.

  Args:
      text (str): The input text to be truncated.
      available_space (int): The available space for the truncated text.
      line_length (int): The total line length.

  Returns:
      str: The truncated text with ellipsis if needed.
  """
  if available_space < len(ELLIPSIS):
    available_space = line_length
  # No need to truncate
  if len(text) <= available_space:
    return text
  return text[:available_space - len(ELLIPSIS)] + ELLIPSIS


def EllipsisMiddleTruncate(text, available_space, line_length):
  """  Truncates text from the middle with ellipsis.

  Args:
      text (str): The input text to be truncated.
      available_space (int): The available space for the truncated text.
      line_length (int): The total line length.

  Returns:
      str: The truncated text with ellipsis in the middle.
  """
  if available_space < len(ELLIPSIS):
    available_space = line_length
  if len(text) < available_space:
    return text
  available_string_len = available_space - len(ELLIPSIS)
  first_half_len = int(available_string_len / 2)  # start from middle
  second_half_len = available_string_len - first_half_len
  return text[:first_half_len] + ELLIPSIS + text[-second_half_len:]


def DoubleQuote(text):
  """Return the input text enclosed in double quotes.

  Args:
      text (str): The input text to be enclosed in double quotes.

  Returns:
      str: The input text enclosed in double quotes.
  """

  return '"%s"' % text
