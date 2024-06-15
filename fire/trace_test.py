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

"""Tests for the trace module."""

from fire import testutils
from fire import trace


class FireTraceTest(testutils.BaseTestCase):

  def testFireTraceInitialization(self):
    """Test the initialization of FireTrace object.

    This function initializes a FireTrace object with a specified size and
    asserts that the object and its elements are not None.

    Args:
        self: The object instance.
    """

    t = trace.FireTrace(10)
    self.assertIsNotNone(t)
    self.assertIsNotNone(t.elements)

  def testFireTraceGetResult(self):
    """Test the GetResult method of the FireTrace class.

    This function creates a FireTrace object with an initial result of
    'start'. It then checks if the initial result is 'start' using the
    GetResult method. Next, it adds an accessed property 't' with a final
    value of None at line 10 in example.py. Finally, it checks if the result
    is now 't' using the GetResult method.
    """

    t = trace.FireTrace('start')
    self.assertEqual(t.GetResult(), 'start')
    t.AddAccessedProperty('t', 'final', None, 'example.py', 10)
    self.assertEqual(t.GetResult(), 't')

  def testFireTraceHasError(self):
    """Test the HasError method of the FireTrace class.

    This method creates a FireTrace object, adds accessed properties, and
    checks if an error is present.
    """

    t = trace.FireTrace('start')
    self.assertFalse(t.HasError())
    t.AddAccessedProperty('t', 'final', None, 'example.py', 10)
    self.assertFalse(t.HasError())
    t.AddError(ValueError('example error'), ['arg'])
    self.assertTrue(t.HasError())

  def testAddAccessedProperty(self):
    """Test the functionality of adding an accessed property to a FireTrace
    object.

    This function creates a FireTrace object with an initial description,
    adds an accessed property to it, and then checks if the string
    representation of the object matches the expected output.

    Args:
        self: The instance of the test case.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddAccessedProperty('new component', 'prop', args, 'sample.py', 12)
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Accessed property "prop" (sample.py:12)')

  def testAddCalledCallable(self):
    """Test the functionality of adding a called callable component to the
    FireTrace object.

    This function creates a FireTrace object with an initial component and
    then adds a called callable component with the provided arguments, file
    name, line number, and action type. It then asserts that the string
    representation of the FireTrace object matches the expected output.

    Args:
        self: The FireTrace test instance.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledComponent('result', 'cell', args, 'sample.py', 10, False,
                         action=trace.CALLED_CALLABLE)
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Called callable "cell" (sample.py:10)')

  def testAddCalledRoutine(self):
    """Test the functionality of adding a called routine to the FireTrace
    object.

    This method creates a FireTrace object, adds a called component to it
    with the specified arguments, and then asserts that the string
    representation of the FireTrace object matches the expected value.

    Args:
        self: The object instance.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledComponent('result', 'run', args, 'sample.py', 12, False,
                         action=trace.CALLED_ROUTINE)
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Called routine "run" (sample.py:12)')

  def testAddInstantiatedClass(self):
    """Test the AddCalledComponent method with INSTANTIATED_CLASS action.

    This method creates a FireTrace object, adds a called component with
    action INSTANTIATED_CLASS, and then checks if the string representation
    of the FireTrace object matches the target string.

    Args:
        self: The test case object.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledComponent(
        'Classname', 'classname', args, 'sample.py', 12, False,
        action=trace.INSTANTIATED_CLASS)
    target = """1. Initial component
2. Instantiated class "classname" (sample.py:12)"""
    self.assertEqual(str(t), target)

  def testAddCompletionScript(self):
    """Test the functionality of adding a completion script to a FireTrace
    object.

    This method creates a FireTrace object with an initial description and
    then adds a completion script to it. It then asserts that the string
    representation of the FireTrace object matches the expected value.
    """

    t = trace.FireTrace('initial object')
    t.AddCompletionScript('This is the completion script string.')
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Generated completion script')

  def testAddInteractiveMode(self):
    """Test the addition of interactive mode to the FireTrace object.

    This function creates a FireTrace object with an initial component and
    adds an interactive mode to it. It then asserts that the string
    representation of the FireTrace object matches the expected value.
    """

    t = trace.FireTrace('initial object')
    t.AddInteractiveMode()
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Entered interactive mode')

  def testGetCommand(self):
    """Test the GetCommand method of the FireTrace class.

    This method adds a called component to the FireTrace object and then
    retrieves the command.

    Returns:
        str: The command generated by the GetCommand method.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledComponent('result', 'run', args, 'sample.py', 12, False,
                         action=trace.CALLED_ROUTINE)
    self.assertEqual(t.GetCommand(), 'example args')

  def testGetCommandWithQuotes(self):
    """Test the GetCommand method of the FireTrace class when arguments contain
    quotes.

    This method creates a FireTrace object with an initial message, adds a
    called component with arguments containing quotes, and then checks if
    the GetCommand method returns the expected command string.

    Returns:
        str: The command string generated by the GetCommand method.
    """

    t = trace.FireTrace('initial object')
    args = ('example', 'spaced arg')
    t.AddCalledComponent('result', 'run', args, 'sample.py', 12, False,
                         action=trace.CALLED_ROUTINE)
    self.assertEqual(t.GetCommand(), "example 'spaced arg'")

  def testGetCommandWithFlagQuotes(self):
    """Test the GetCommand method when the argument contains a flag with
    quotes.

    This method creates a FireTrace object, adds a called component with
    arguments containing a spaced flag, and then asserts that the GetCommand
    method returns the correct command string.

    Args:
        self: The object instance.
    """

    t = trace.FireTrace('initial object')
    args = ('--example=spaced arg',)
    t.AddCalledComponent('result', 'run', args, 'sample.py', 12, False,
                         action=trace.CALLED_ROUTINE)
    self.assertEqual(t.GetCommand(), "--example='spaced arg'")


class FireTraceElementTest(testutils.BaseTestCase):

  def testFireTraceElementHasError(self):
    """Test the HasError method of FireTraceElement.

    This function tests the HasError method of the FireTraceElement class by
    creating instances of FireTraceElement with and without errors, and then
    asserting the expected behavior.
    """

    el = trace.FireTraceElement()
    self.assertFalse(el.HasError())

    el = trace.FireTraceElement(error=ValueError('example error'))
    self.assertTrue(el.HasError())

  def testFireTraceElementAsStringNoMetadata(self):
    """Test the string representation of a FireTraceElement without metadata.

    This function creates a FireTraceElement object with the specified
    component and action. It then asserts that the string representation of
    the object is equal to the action.

    Args:
        self: The test case instance.
    """

    el = trace.FireTraceElement(
        component='Example',
        action='Fake action',
    )
    self.assertEqual(str(el), 'Fake action')

  def testFireTraceElementAsStringWithTarget(self):
    """Test the string representation of a FireTraceElement with a target.

    This function creates a FireTraceElement object with the specified
    component, action, and target. It then asserts that the string
    representation of the object is as expected.
    """

    el = trace.FireTraceElement(
        component='Example',
        action='Created toy',
        target='Beaker',
    )
    self.assertEqual(str(el), 'Created toy "Beaker"')

  def testFireTraceElementAsStringWithTargetAndLineNo(self):
    """Test the string representation of a FireTraceElement with target and
    line number.

    This function creates a FireTraceElement object with the specified
    component, action, target, filename, and line number. It then asserts
    that the string representation of the object matches the expected
    format.
    """

    el = trace.FireTraceElement(
        component='Example',
        action='Created toy',
        target='Beaker',
        filename='beaker.py',
        lineno=10,
    )
    self.assertEqual(str(el), 'Created toy "Beaker" (beaker.py:10)')


if __name__ == '__main__':
  testutils.main()
