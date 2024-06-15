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

"""Test the test utilities for Fire's tests."""

import sys

from fire import testutils

import six


class TestTestUtils(testutils.BaseTestCase):
  """Let's get meta."""

  def testNoCheckOnException(self):
    """Test that no check is performed on the raised exception.

    This test case uses the assertRaises context manager to check if a
    ValueError is raised. It also uses the assertOutputMatches context
    manager to match the standard output with 'blah'.
    """

    with self.assertRaises(ValueError):
      with self.assertOutputMatches(stdout='blah'):
        raise ValueError()

  def testCheckStdoutOrStderrNone(self):
    """Test the behavior of assertOutputMatches when stdout or stderr is set to
    None.

    This function tests the behavior of assertOutputMatches when stdout or
    stderr is set to None. It checks if the function raises AssertionError
    with the appropriate message when stdout or stderr is None.
    """

    with six.assertRaisesRegex(self, AssertionError, 'stdout:'):
      with self.assertOutputMatches(stdout=None):
        print('blah')

    with six.assertRaisesRegex(self, AssertionError, 'stderr:'):
      with self.assertOutputMatches(stderr=None):
        print('blah', file=sys.stderr)

    with six.assertRaisesRegex(self, AssertionError, 'stderr:'):
      with self.assertOutputMatches(stdout='apple', stderr=None):
        print('apple')
        print('blah', file=sys.stderr)

  def testCorrectOrderingOfAssertRaises(self):
    """Test the correct ordering of assertRaises in the context of FireExit
    tests.

    This function checks whether the FireExit tests are in the correct
    order. It uses assertOutputMatches to match the stdout with a specific
    pattern. It then checks if a ValueError is raised in the expected
    scenario.
    """

    # Check to make sure FireExit tests are correct.
    with self.assertOutputMatches(stdout='Yep.*first.*second'):
      with self.assertRaises(ValueError):
        print('Yep, this is the first line.\nThis is the second.')
        raise ValueError()


if __name__ == '__main__':
  testutils.main()
