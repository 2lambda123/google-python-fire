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

"""Tests for the inspectutils module."""

import os
import unittest

from fire import inspectutils
from fire import test_components as tc
from fire import testutils

import six


class InspectUtilsTest(testutils.BaseTestCase):

  def testGetFullArgSpec(self):
    """Test the GetFullArgSpec function from inspectutils module.

    This function tests the GetFullArgSpec function by checking various
    attributes of the returned object.
    """

    spec = inspectutils.GetFullArgSpec(tc.identity)
    self.assertEqual(spec.args, ['arg1', 'arg2', 'arg3', 'arg4'])
    self.assertEqual(spec.defaults, (10, 20))
    self.assertEqual(spec.varargs, 'arg5')
    self.assertEqual(spec.varkw, 'arg6')
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {'arg2': int, 'arg4': int})

  @unittest.skipIf(six.PY2, 'No keyword arguments in python 2')
  def testGetFullArgSpecPy3(self):
    """Test the GetFullArgSpec function for Python 3.

    This function tests the GetFullArgSpec function by checking various
    attributes of the returned object.
    """

    spec = inspectutils.GetFullArgSpec(tc.py3.identity)
    self.assertEqual(spec.args, ['arg1', 'arg2', 'arg3', 'arg4'])
    self.assertEqual(spec.defaults, (10, 20))
    self.assertEqual(spec.varargs, 'arg5')
    self.assertEqual(spec.varkw, 'arg10')
    self.assertEqual(spec.kwonlyargs, ['arg6', 'arg7', 'arg8', 'arg9'])
    self.assertEqual(spec.kwonlydefaults, {'arg8': 30, 'arg9': 40})
    self.assertEqual(spec.annotations,
                     {'arg2': int, 'arg4': int, 'arg7': int, 'arg9': int})

  def testGetFullArgSpecFromBuiltin(self):
    """Test the function GetFullArgSpec with a built-in function.

    This function tests the GetFullArgSpec function by passing a built-in
    function 'test'.upper and then asserts the returned values against the
    expected values.

    Args:
        self: The instance of the test case.
    """

    spec = inspectutils.GetFullArgSpec('test'.upper)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromSlotWrapper(self):
    """Test the function GetFullArgSpecFromSlotWrapper.

    This function tests the GetFullArgSpecFromSlotWrapper function by
    calling it with a specific input and checking the output against
    expected values.

    Args:
        self: The object instance.
    """

    spec = inspectutils.GetFullArgSpec(tc.NoDefaults)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromNamedTuple(self):
    """Test the function GetFullArgSpecFromNamedTuple from the inspectutils
    module.

    This function retrieves the full argument specification of a named tuple
    class. It checks the arguments, defaults, variable arguments, variable
    keyword arguments, keyword-only arguments, keyword-only defaults, and
    annotations of the named tuple class.
    """

    spec = inspectutils.GetFullArgSpec(tc.NamedTuplePoint)
    self.assertEqual(spec.args, ['x', 'y'])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromNamedTupleSubclass(self):
    """Test the function GetFullArgSpec with a NamedTuple subclass.

    This function tests the GetFullArgSpec function with a NamedTuple
    subclass to ensure it returns the correct argument specifications.

    Args:
        self: The test case object.
    """

    spec = inspectutils.GetFullArgSpec(tc.SubPoint)
    self.assertEqual(spec.args, ['x', 'y'])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromClassNoInit(self):
    """Test the function GetFullArgSpec to retrieve the full argument
    specification from a class without __init__ method.

    This function calls GetFullArgSpec with a class that does not have an
    __init__ method and asserts the returned values for various attributes
    of the argument specification.
    """

    spec = inspectutils.GetFullArgSpec(tc.OldStyleEmpty)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromMethod(self):
    """Test the function GetFullArgSpecFromMethod in the inspectutils module.

    This function tests the GetFullArgSpecFromMethod function by passing a
    method with no default arguments. It checks the returned FullArgSpec
    object for various attributes such as args, defaults, varargs, varkw,
    kwonlyargs, kwonlydefaults, and annotations.

    Args:
        self: The instance of the test case.
    """

    spec = inspectutils.GetFullArgSpec(tc.NoDefaults().double)
    self.assertEqual(spec.args, ['count'])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testInfoOne(self):
    """Test the Info class with input value 1.

    This function creates an instance of the Info class with input value 1
    and then performs several assertions to check the attributes of the Info
    object.
    """

    info = inspectutils.Info(1)
    self.assertEqual(info.get('type_name'), 'int')
    self.assertEqual(info.get('file'), None)
    self.assertEqual(info.get('line'), None)
    self.assertEqual(info.get('string_form'), '1')

  def testInfoClass(self):
    """Test the Info class from inspectutils module.

    This function creates an instance of the Info class using the
    tc.NoDefaults object and performs various assertions on the information
    retrieved from the object.

    Args:
        self: The test case instance.
    """

    info = inspectutils.Info(tc.NoDefaults)
    self.assertEqual(info.get('type_name'), 'type')
    self.assertIn(os.path.join('fire', 'test_components.py'), info.get('file'))
    self.assertGreater(info.get('line'), 0)

  def testInfoClassNoInit(self):
    """Test the Info class when no __init__ method is defined.

    This function creates an instance of the Info class with the input
    parameter tc.OldStyleEmpty. It then checks the type_name attribute of
    the instance based on the Python version. Additionally, it verifies that
    the file attribute contains the path 'fire/test_components.py' and that
    the line attribute is greater than 0.

    Args:
        self: The test case instance.
    """

    info = inspectutils.Info(tc.OldStyleEmpty)
    if six.PY2:
      self.assertEqual(info.get('type_name'), 'classobj')
    else:
      self.assertEqual(info.get('type_name'), 'type')
    self.assertIn(os.path.join('fire', 'test_components.py'), info.get('file'))
    self.assertGreater(info.get('line'), 0)

  def testInfoNoDocstring(self):
    """This function tests the Info class with a case where no docstring is
    present.

    Args:
        self: The object instance.
    """

    info = inspectutils.Info(tc.NoDefaults)
    self.assertEqual(info['docstring'], None, 'Docstring should be None')


if __name__ == '__main__':
  testutils.main()
