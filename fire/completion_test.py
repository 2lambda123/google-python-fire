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

"""Tests for the completion module."""

from fire import completion
from fire import test_components as tc
from fire import testutils


class TabCompletionTest(testutils.BaseTestCase):

  def testCompletionBashScript(self):
    """A sanity check test to ensure the bash completion script meets basic
    assumptions.

    This function creates a bash completion script with predefined commands
    and asserts their presence.

    Args:
        self: The test class instance.
    """

    # A sanity check test to make sure the bash completion script satisfies
    # some basic assumptions.
    commands = [
        ['run'],
        ['halt'],
        ['halt', '--now'],
    ]
    script = completion._BashScript(name='command', commands=commands)  # pylint: disable=protected-access
    self.assertIn('command', script)
    self.assertIn('halt', script)

    assert_template = '{command})'
    for last_command in ['command', 'halt']:
      self.assertIn(assert_template.format(command=last_command), script)

  def testCompletionFishScript(self):
    """A sanity check test to ensure the fish completion script meets basic
    assumptions.

    This test checks the behavior of the fish completion script by creating
    a script with predefined commands and then asserts the presence of these
    commands in the generated script.
    """

    # A sanity check test to make sure the fish completion script satisfies
    # some basic assumptions.
    commands = [
        ['run'],
        ['halt'],
        ['halt', '--now'],
    ]
    script = completion._FishScript(name='command', commands=commands)  # pylint: disable=protected-access
    self.assertIn('command', script)
    self.assertIn('halt', script)
    self.assertIn('-l now', script)

  def testFnCompletions(self):
    """Test the Completions class with an example function.

    This function creates an example function that takes three arguments and
    returns them. It then creates an instance of the Completions class with
    the example function and checks for the presence of '--one', '--two',
    and '--three' in the completions.

    Args:
        self: The instance of the test class.
    """

    def example(one, two, three):
      """Return the three input values.

      This function takes in three input values and returns them as a tuple.

      Args:
          one: The first input value.
          two: The second input value.
          three: The third input value.

      Returns:
          tuple: A tuple containing the three input values.
      """

      return one, two, three

    completions = completion.Completions(example)
    self.assertIn('--one', completions)
    self.assertIn('--two', completions)
    self.assertIn('--three', completions)

  def testListCompletions(self):
    """Test the Completions class with a list of values.

    It initializes the Completions class with a list of values and then
    checks if the indices are present or not.

    Args:
        self: The object instance.
    """

    completions = completion.Completions(['red', 'green', 'blue'])
    self.assertIn('0', completions)
    self.assertIn('1', completions)
    self.assertIn('2', completions)
    self.assertNotIn('3', completions)

  def testDictCompletions(self):
    """Test the Completions class with a dictionary input.

    This function creates a Completions object from a dictionary of colors
    and performs various assertions to check the behavior.

    Args:
        self: The object instance.
    """

    colors = {
        'red': 'green',
        'blue': 'yellow',
        '_rainbow': True,
    }
    completions = completion.Completions(colors)
    self.assertIn('red', completions)
    self.assertIn('blue', completions)
    self.assertNotIn('green', completions)
    self.assertNotIn('yellow', completions)
    self.assertNotIn('_rainbow', completions)
    self.assertNotIn('True', completions)
    self.assertNotIn(True, completions)

  def testDictCompletionsVerbose(self):
    """Test the Completions class with a dictionary of colors in verbose mode.

    It creates a dictionary of colors and initializes the Completions object
    with verbose set to True. Then it checks if the keys of the colors
    dictionary are present in the completions and if the values are not
    present.

    Args:
        self: The test case object.
    """

    colors = {
        'red': 'green',
        'blue': 'yellow',
        '_rainbow': True,
    }
    completions = completion.Completions(colors, verbose=True)
    self.assertIn('red', completions)
    self.assertIn('blue', completions)
    self.assertNotIn('green', completions)
    self.assertNotIn('yellow', completions)
    self.assertIn('_rainbow', completions)
    self.assertNotIn('True', completions)
    self.assertNotIn(True, completions)

  def testDeepDictCompletions(self):
    """Test the Completions class with a deep dictionary.

    This function creates a deep dictionary with multiple levels and
    initializes a Completions object with it. It then checks if certain keys
    are present or absent in the Completions object.

    Args:
        self: The test case object.
    """

    deepdict = {'level1': {'level2': {'level3': {'level4': {}}}}}
    completions = completion.Completions(deepdict)
    self.assertIn('level1', completions)
    self.assertNotIn('level2', completions)

  def testDeepDictScript(self):
    """Test the functionality of creating a deep dictionary script.

    It creates a deep dictionary with multiple nested levels and checks if
    the script contains the expected keys at different depths.
    """

    deepdict = {'level1': {'level2': {'level3': {'level4': {}}}}}
    script = completion.Script('deepdict', deepdict)
    self.assertIn('level1', script)
    self.assertIn('level2', script)
    self.assertIn('level3', script)
    self.assertNotIn('level4', script)  # The default depth is 3.

  def testFnScript(self):
    """Test the generation of a script with specific arguments for the
    'identity' function.

    This function creates a script using the 'identity' function and checks
    if specific arguments are present in the script.

    Args:
        self: The instance of the test class.
    """

    script = completion.Script('identity', tc.identity)
    self.assertIn('--arg1', script)
    self.assertIn('--arg2', script)
    self.assertIn('--arg3', script)
    self.assertIn('--arg4', script)

  def testClassScript(self):
    """Test the functionality of the Script class.

    This function creates an instance of the Script class with an empty
    string and MixedDefaults configuration. It then asserts the presence of
    specific attributes in the script instance.

    Args:
        self: The instance of the test case.
    """

    script = completion.Script('', tc.MixedDefaults)
    self.assertIn('ten', script)
    self.assertIn('sum', script)
    self.assertIn('identity', script)
    self.assertIn('--alpha', script)
    self.assertIn('--beta', script)

  def testDeepDictFishScript(self):
    """Test the behavior of the Script class with a deep dictionary for the
    Fish shell.

    It creates a deep dictionary with multiple levels and initializes a
    Script object with the dictionary and the shell set to 'fish'. It then
    asserts the presence of keys at different levels in the script and
    checks that a key at a deeper level is not present.
    """

    deepdict = {'level1': {'level2': {'level3': {'level4': {}}}}}
    script = completion.Script('deepdict', deepdict, shell='fish')
    self.assertIn('level1', script)
    self.assertIn('level2', script)
    self.assertIn('level3', script)
    self.assertNotIn('level4', script)  # The default depth is 3.

  def testFnFishScript(self):
    """Test the generation of a completion script for the fish shell.

    This function creates a completion script using the 'identity' command
    and checks if the script contains specific arguments.

    Args:
        self: The test class instance.
    """

    script = completion.Script('identity', tc.identity, shell='fish')
    self.assertIn('arg1', script)
    self.assertIn('arg2', script)
    self.assertIn('arg3', script)
    self.assertIn('arg4', script)

  def testClassFishScript(self):
    """Test the Script class with Fish shell configuration.

    This function creates a Script object with empty input, MixedDefaults
    configuration, and Fish shell. It then asserts the presence of specific
    commands in the generated script.

    Args:
        self: The test case object.
    """

    script = completion.Script('', tc.MixedDefaults, shell='fish')
    self.assertIn('ten', script)
    self.assertIn('sum', script)
    self.assertIn('identity', script)
    self.assertIn('alpha', script)
    self.assertIn('beta', script)

  def testNonStringDictCompletions(self):
    """Test the Completions class with a dictionary containing non-string keys.

    This function creates an instance of the Completions class with a
    dictionary containing non-string keys. It then asserts that the keys are
    correctly converted to strings and present in the completions, while the
    original values are not present.

    Args:
        self: The instance of the test case.
    """

    completions = completion.Completions({
        10: 'green',
        3.14: 'yellow',
        ('t1', 't2'): 'pink',
    })
    self.assertIn('10', completions)
    self.assertIn('3.14', completions)
    self.assertIn("('t1', 't2')", completions)
    self.assertNotIn('green', completions)
    self.assertNotIn('yellow', completions)
    self.assertNotIn('pink', completions)

  def testGeneratorCompletions(self):
    """Test the Completions class with a generator function.

    This function creates a generator that yields incremental values
    starting from 0. It then initializes a Completions object with the
    generated values and asserts that it is an empty list.
    """

    def generator():
      """Generator function that yields consecutive integers starting from 0.

      Yields integers starting from 0 incrementing by 1 each time it is
      called.

      Yields:
          int: Consecutive integers starting from 0.
      """

      x = 0
      while True:
        yield x
        x += 1
    completions = completion.Completions(generator())
    self.assertEqual(completions, [])

  def testClassCompletions(self):
    """Test the Completions class with a TestCase that has no default values.

    This function creates an instance of the Completions class with a
    TestCase that has no default values. It then asserts that the
    completions list is empty.

    Args:
        self: The TestCase instance.
    """

    completions = completion.Completions(tc.NoDefaults)
    self.assertEqual(completions, [])

  def testObjectCompletions(self):
    """Test object completions for a given test case.

    This function initializes completions for a test case with no defaults,
    checks if 'double' and 'triple' are present in the completions.

    Args:
        self: Test case object.
    """

    completions = completion.Completions(tc.NoDefaults())
    self.assertIn('double', completions)
    self.assertIn('triple', completions)

  def testMethodCompletions(self):
    """Test the method completions for a given object.

    This function creates completions for a specific object and asserts the
    presence of certain completion options.

    Args:
        self: The object being tested.
    """

    completions = completion.Completions(tc.NoDefaults().double)
    self.assertNotIn('--self', completions)
    self.assertIn('--count', completions)


if __name__ == '__main__':
  testutils.main()
