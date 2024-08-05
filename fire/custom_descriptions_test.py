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

"""Tests for custom description module."""

from fire import custom_descriptions
from fire import testutils

LINE_LENGTH = 80


class CustomDescriptionTest(testutils.BaseTestCase):

  def test_string_type_summary_enough_space(self):
    """Test the function GetSummary with a string component and enough
    available space.

    This function tests the GetSummary function by providing a string
    component and ensuring that the summary generated has quotes around it.

    Args:
        self: The test case object.
    """

    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=80, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Test"')

  def test_string_type_summary_not_enough_space_truncated(self):
    """Test the behavior of GetSummary function when the available space is not
    enough to display the full summary.

    This function tests the behavior of the GetSummary function when the
    available space is insufficient to display the full summary. It sets up
    a component name and calls the GetSummary function with limited
    available space and a specified line length. The expected behavior is
    that the summary should be truncated with ellipsis ("...").

    Args:
        self: The test case object.
    """

    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=5, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"..."')

  def test_string_type_summary_not_enough_space_new_line(self):
    """Test the GetSummary function with a string type input where there is not
    enough space for a new line.

    Args:
        obj (str): The input string to be summarized.
        available_space (int): The available space for the summary.
        line_length (int): The maximum length of a line in the summary.

    Returns:
        str: The summarized string.
    """

    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=4, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Test"')

  def test_string_type_summary_not_enough_space_long_truncated(self):
    """Test the GetSummary function when the input string is too long to fit
    within the available space.

    This function tests the behavior of the GetSummary function when the
    input string is longer than the available space and needs to be
    truncated to fit within the specified length.

    Args:
        self: The test case object.
    """

    component = 'Lorem ipsum dolor sit amet'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Lorem..."')

  def test_string_type_description_enough_space(self):
    """Test the description generation for a string with enough space
    available.

    This function tests the custom description generation for a given
    component string when there is enough available space provided. It
    checks if the generated description matches the expected description.

    Args:
        self: The test case object.
    """

    component = 'Test'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=80, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Test"')

  def test_string_type_description_not_enough_space_truncated(self):
    """Test the truncation of a string description when there is not enough
    space available.

    This function tests the behavior of truncating a string description when
    the available space is limited.

    Args:
        self: The test case object.
    """

    component = 'Lorem ipsum dolor sit amet'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=20, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Lore..."')

  def test_string_type_description_not_enough_space_new_line(self):
    """Test the function GetDescription with a string type input where the
    description does not have enough space for a new line.

    Args:
        self: The object instance.
    """

    component = 'Lorem ipsum dolor sit amet'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Lorem ipsum dolor sit amet"')


if __name__ == '__main__':
  testutils.main()
