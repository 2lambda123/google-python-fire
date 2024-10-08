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

"""Types of values."""

import inspect

from fire import inspectutils
import six


VALUE_TYPES = (bool, six.string_types, six.integer_types, float, complex,
               type(Ellipsis), type(None), type(NotImplemented))


def IsGroup(component):
  """Check if the given component is a group.

  This function checks if the given component is a group by verifying that
  it is neither a command nor a value.

  Args:
      component: The component to be checked.

  Returns:
      bool: True if the component is a group, False otherwise.
  """

  # TODO(dbieber): Check if there are any subcomponents.
  return not IsCommand(component) and not IsValue(component)


def IsCommand(component):
  """Check if the given component is a command.

  This function checks if the input component is a routine (function or
  method) or a class.

  Args:
      component: Any Python object to be checked.

  Returns:
      bool: True if the component is a routine or a class, False otherwise.
  """

  return inspect.isroutine(component) or inspect.isclass(component)


def IsValue(component):
  """Check if the input component is a value type or has a custom __str__
  method.

  Args:
      component: Any Python object to be checked.

  Returns:
      bool: True if the component is of a value type or has a custom __str__ method,
          False otherwise.
  """

  return isinstance(component, VALUE_TYPES) or HasCustomStr(component)


def IsSimpleGroup(component):
  """  If a group is simple enough, then we treat it as a value in PrintResult.

  Only if a group contains all value types do we consider it simple enough
  to print as a value.

  Args:
      component (dict): The group to check for value-group status.

  Returns:
      bool: A boolean indicating if the group should be treated as a value for
          printing purposes.
  """
  assert isinstance(component, dict)
  for unused_key, value in component.items():
    if not IsValue(value) and not isinstance(value, (list, dict)):
      return False
  return True


def HasCustomStr(component):
  """  Determines if a component has a custom __str__ method.

  Uses inspect.classify_class_attrs to determine the origin of the
  object's __str__ method, if one is present. If it is defined by `object`
  itself, then it is not considered custom. Otherwise, it is. This means
  that the __str__ methods of primitives like ints and floats are
  considered custom.  Objects with custom __str__ methods are treated as
  values and can be serialized in places where more complex objects would
  have their help screen shown instead.

  Args:
      component: The object to check for a custom __str__ method.

  Returns:
      bool: Whether `component` has a custom __str__ method.
  """
  if hasattr(component, '__str__'):
    class_attrs = inspectutils.GetClassAttrsDict(type(component)) or {}
    str_attr = class_attrs.get('__str__')
    if str_attr and str_attr.defining_class is not object:
      return True
  return False
