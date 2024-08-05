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

"""These decorators provide function metadata to Python Fire.

SetParseFn and SetParseFns allow you to set the functions Fire uses for parsing
command line arguments to client code.
"""

import inspect

FIRE_METADATA = 'FIRE_METADATA'
FIRE_PARSE_FNS = 'FIRE_PARSE_FNS'
ACCEPTS_POSITIONAL_ARGS = 'ACCEPTS_POSITIONAL_ARGS'


def SetParseFn(fn, *arguments):
  """  Sets the function for Fire to use to parse arguments when calling the
  decorated function.

  This function sets the parse function for Fire to use when parsing
  arguments for the decorated function. If no specific arguments are
  provided, it sets the default parse function.

  Args:
      fn: The function to be used for parsing arguments.
      *arguments: The arguments for which to use the parse function.

  Returns:
      function: The decorated function, which now has metadata telling Fire how to
          perform.
  """
  def _Decorator(func):
    """Decorator function for setting parse functions for arguments in a
    command line interface.

    This decorator function sets parse functions for arguments in a command
    line interface. It checks if arguments are provided, and if not, sets
    the default parse function. If arguments are provided, it sets parse
    functions for each named argument.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function with parse functions set for arguments.
    """

    parse_fns = GetParseFns(func)
    if not arguments:
      parse_fns['default'] = fn
    else:
      for argument in arguments:
        parse_fns['named'][argument] = fn
    _SetMetadata(func, FIRE_PARSE_FNS, parse_fns)
    return func

  return _Decorator


def SetParseFns(*positional, **named):
  """  Set the functions for Fire to use to parse arguments when calling the
  decorated function.

  Returns a decorator that, when applied to a function, adds metadata to
  the function indicating how Fire should convert string command line
  arguments into valid Python arguments for calling the function.  A parse
  function should take a single string argument and return a value to be
  used in place when calling the decorated function.

  Args:
      *positional: The functions to be used for parsing positional arguments.
      **named: The functions to be used for parsing named arguments.

  Returns:
      function: The decorated function, now with metadata indicating how Fire should
          perform.
  """
  def _Decorator(fn):
    """Decorator function to update the parsing functions for a given function.

    This decorator function updates the parsing functions for a given
    function based on the provided positional and named arguments.

    Args:
        fn (function): The function to be decorated.
        positional (list): List of positional arguments.
        named (dict): Dictionary of named arguments.

    Returns:
        function: The decorated function with updated parsing functions.
    """

    parse_fns = GetParseFns(fn)
    parse_fns['positional'] = positional
    parse_fns['named'].update(named)  # pytype: disable=attribute-error
    _SetMetadata(fn, FIRE_PARSE_FNS, parse_fns)
    return fn

  return _Decorator


def _SetMetadata(fn, attribute, value):
  """Set metadata attribute for a given function.

  This function sets a specific metadata attribute with a value for the
  given function.

  Args:
      fn (function): The function for which metadata attribute needs to be set.
      attribute (str): The attribute to be set in the metadata.
      value: The value to be assigned to the attribute.
  """

  metadata = GetMetadata(fn)
  metadata[attribute] = value
  setattr(fn, FIRE_METADATA, metadata)


def GetMetadata(fn):
  # type: (...) -> dict
  """  Gets metadata attached to the function `fn` as an attribute.

  This function retrieves metadata attached to the input function `fn` and
  returns it as a dictionary.

  Args:
      fn: The function from which to retrieve the function metadata.

  Returns:
      dict: A dictionary mapping property strings to their value.
  """
  # Class __init__ functions and object __call__ functions require flag style
  # arguments. Other methods and functions may accept positional args.
  default = {
      ACCEPTS_POSITIONAL_ARGS: inspect.isroutine(fn),
  }
  try:
    metadata = getattr(fn, FIRE_METADATA, default)
    if ACCEPTS_POSITIONAL_ARGS in metadata:
      return metadata
    else:
      return default
  except:  # pylint: disable=bare-except
    return default


def GetParseFns(fn):
  """Get the parsing functions for a given function.

  This function retrieves the parsing functions associated with the input
  function.

  Args:
      fn: The input function for which parsing functions are to be retrieved.

  Returns:
      dict: A dictionary containing parsing functions with keys 'default',
          'positional', and 'named'.
  """

  # type: (...) -> dict
  metadata = GetMetadata(fn)
  default = {"default": None, "positional": [], "named": {}}
  return metadata.get(FIRE_PARSE_FNS, default)
