# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Some general file utilities used that can be used by the Cloud SDK."""

import os

from fire.console import encoding as encoding_util
from fire.console import platforms

import six


def _GetSystemPath():
  """  Returns properly encoded system PATH variable string.

  This function retrieves the system PATH variable and returns it as a
  properly encoded string.

  Returns:
      str: The system PATH variable string.
  """
  return encoding_util.GetEncodedValue(os.environ, 'PATH')


def _FindExecutableOnPath(executable, path, pathext):
  """  Internal function to find an executable on the specified path.
  """

  if isinstance(pathext, six.string_types):
    raise ValueError('_FindExecutableOnPath(..., pathext=\'{0}\') failed '
                     'because pathext must be an iterable of strings, but got '
                     'a string.'.format(pathext))

  # Prioritize preferred extension over earlier in path.
  for ext in pathext:
    for directory in path.split(os.pathsep):
      # Windows can have paths quoted.
      directory = directory.strip('"')
      full = os.path.normpath(os.path.join(directory, executable) + ext)
      # On Windows os.access(full, os.X_OK) is always True.
      if os.path.isfile(full) and os.access(full, os.X_OK):
        return full
  return None


def _PlatformExecutableExtensions(platform):
  """Return the executable extensions based on the platform.

  This function takes a platform as input and returns a tuple of
  executable extensions based on the platform type. For Windows platform,
  it returns ('.exe', '.cmd', '.bat', '.com', '.ps1'), and for other
  platforms, it returns ('', '.sh').

  Args:
      platform (str): The platform type.

  Returns:
      tuple: A tuple of executable extensions based on the platform.
  """

  if platform == platforms.OperatingSystem.WINDOWS:
    return ('.exe', '.cmd', '.bat', '.com', '.ps1')
  else:
    return ('', '.sh')


def FindExecutableOnPath(executable, path=None, pathext=None,
                         allow_extensions=False):
  """  Searches for `executable` in the directories listed in `path` or $PATH.

  Executable must not contain a directory or an extension.
  """

  if not allow_extensions and os.path.splitext(executable)[1]:
    raise ValueError('FindExecutableOnPath({0},...) failed because first '
                     'argument must not have an extension.'.format(executable))

  if os.path.dirname(executable):
    raise ValueError('FindExecutableOnPath({0},...) failed because first '
                     'argument must not have a path.'.format(executable))

  if path is None:
    effective_path = _GetSystemPath()
  else:
    effective_path = path
  effective_pathext = (pathext if pathext is not None
                       else _PlatformExecutableExtensions(
                           platforms.OperatingSystem.Current()))

  return _FindExecutableOnPath(executable, effective_path,
                               effective_pathext)
