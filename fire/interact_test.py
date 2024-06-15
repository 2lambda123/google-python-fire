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

"""Tests for the interact module."""

from fire import interact
from fire import testutils

import mock


try:
  import IPython  # pylint: disable=unused-import, g-import-not-at-top
  INTERACT_METHOD = 'IPython.start_ipython'
except ImportError:
  INTERACT_METHOD = 'code.InteractiveConsole'


class InteractTest(testutils.BaseTestCase):

  @mock.patch(INTERACT_METHOD)
  def testInteract(self, mock_interact_method):
    """Test the interaction method.

    This function tests the interaction method by asserting that the mock
    interact method has not been called, then calling the interact method
    with an empty dictionary, and finally asserting that the mock interact
    method has been called.

    Args:
        mock_interact_method: Mock object representing the interact method.
    """

    self.assertFalse(mock_interact_method.called)
    interact.Embed({})
    self.assertTrue(mock_interact_method.called)

  @mock.patch(INTERACT_METHOD)
  def testInteractVariables(self, mock_interact_method):
    """Test the interaction of variables.

    This function tests the interaction of variables by checking if the
    mock_interact_method is called before and after creating an instance of
    interact.Embed with specific parameters.

    Args:
        mock_interact_method: A mock method for interaction.
    """

    self.assertFalse(mock_interact_method.called)
    interact.Embed({
        'count': 10,
        'mock': mock,
    })
    self.assertTrue(mock_interact_method.called)

if __name__ == '__main__':
  testutils.main()
