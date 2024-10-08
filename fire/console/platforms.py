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

"""Utilities for determining the current platform and architecture."""

import os
import platform
import subprocess
import sys


class Error(Exception):
  """Base class for exceptions in the platforms module."""
  pass


class InvalidEnumValue(Error):  # pylint: disable=g-bad-exception-name
  """Exception for when a string could not be parsed to a valid enum value."""

  def __init__(self, given, enum_type, options):
    """Constructs a new exception.

    Args:
      given: str, The given string that could not be parsed.
      enum_type: str, The human readable name of the enum you were trying to
        parse.
      options: list(str), The valid values for this enum.
    """
    super(InvalidEnumValue, self).__init__(
        'Could not parse [{0}] into a valid {1}.  Valid values are [{2}]'
        .format(given, enum_type, ', '.join(options)))


class OperatingSystem(object):
  """An enum representing the operating system you are running on."""

  class _OS(object):
    """A single operating system."""

    # pylint: disable=redefined-builtin
    def __init__(self, id, name, file_name):
      self.id = id
      self.name = name
      self.file_name = file_name

    def __str__(self):
      """Return the string representation of the object's id.

      This method returns the string representation of the object's id
      attribute.

      Returns:
          str: The string representation of the object's id.
      """

      return self.id

    def __eq__(self, other):
      """Check if two objects are equal based on their id, name, and file_name
      attributes.

      Args:
          other (object): The object to compare with.

      Returns:
          bool: True if the objects are equal, False otherwise.
      """

      return (isinstance(other, type(self)) and
              self.id == other.id and
              self.name == other.name and
              self.file_name == other.file_name)

    def __hash__(self):
      """Return the hash value of the object based on its id, name, and file_name
      attributes.

      This method calculates the hash value by summing the hash values of the
      id, name, and file_name attributes.

      Returns:
          int: The hash value of the object.
      """

      return hash(self.id) + hash(self.name) + hash(self.file_name)

    def __ne__(self, other):
      """Check if two objects are not equal.

      This method checks if the current object is not equal to the other
      object by using the __eq__ method.

      Args:
          self: The current object.
          other: The other object to compare with.

      Returns:
          bool: True if the objects are not equal, False otherwise.
      """

      return not self == other

    @classmethod
    def _CmpHelper(cls, x, y):
      """      Just a helper equivalent to the cmp() function in Python 2.

      Args:
          cls: Class instance.
          x: First value for comparison.
          y: Second value for comparison.

      Returns:
          int: Returns -1 if x < y, 0 if x == y, and 1 if x > y.
      """
      return (x > y) - (x < y)

    def __lt__(self, other):
      """Compare this object with another object based on id, name, and file_name
      attributes.

      Args:
          self (object): The current object.
          other (object): The object to compare with.

      Returns:
          bool: True if the current object is less than the other object, False
              otherwise.
      """

      return self._CmpHelper(
          (self.id, self.name, self.file_name),
          (other.id, other.name, other.file_name)) < 0

    def __gt__(self, other):
      """Compares the current object with another object based on id, name, and
      file_name attributes.

      Args:
          self: An instance of the class.
          other: Another instance of the class to compare with.

      Returns:
          bool: True if the current object is greater than the other object, False
              otherwise.
      """

      return self._CmpHelper(
          (self.id, self.name, self.file_name),
          (other.id, other.name, other.file_name)) > 0

    def __le__(self, other):
      """Returns True if the object is less than or equal to the 'other' object.

      This method is used to implement the less than or equal to comparison
      operator (<=) for custom objects.

      Args:
          self: The current object.
          other: The object to compare against.

      Returns:
          bool: True if the current object is less than or equal to the 'other' object,
              False otherwise.
      """

      return not self.__gt__(other)

    def __ge__(self, other):
      """Special method to determine if the object is greater than or equal to
      another object.

      Args:
          self: The first object to compare.
          other: The second object to compare.

      Returns:
          bool: True if the first object is greater than or equal to the second object,
              False otherwise.
      """

      return not self.__lt__(other)

  WINDOWS = _OS('WINDOWS', 'Windows', 'windows')
  MACOSX = _OS('MACOSX', 'Mac OS X', 'darwin')
  LINUX = _OS('LINUX', 'Linux', 'linux')
  CYGWIN = _OS('CYGWIN', 'Cygwin', 'cygwin')
  MSYS = _OS('MSYS', 'Msys', 'msys')
  _ALL = [WINDOWS, MACOSX, LINUX, CYGWIN, MSYS]

  @staticmethod
  def AllValues():
    """    Gets all possible enum values.

    Returns:
        list: All the enum values.
    """
    return list(OperatingSystem._ALL)

  @staticmethod
  def FromId(os_id, error_on_unknown=True):
    """    Gets the enum corresponding to the given operating system id.
    """
    if not os_id:
      return None
    for operating_system in OperatingSystem._ALL:
      if operating_system.id == os_id:
        return operating_system
    if error_on_unknown:
      raise InvalidEnumValue(os_id, 'Operating System',
                             [value.id for value in OperatingSystem._ALL])
    return None

  @staticmethod
  def Current():
    """    Determines the current operating system.

    Returns:
        OperatingSystemTuple: One of the OperatingSystem constants or None if it cannot be determined.
    """
    if os.name == 'nt':
      return OperatingSystem.WINDOWS
    elif 'linux' in sys.platform:
      return OperatingSystem.LINUX
    elif 'darwin' in sys.platform:
      return OperatingSystem.MACOSX
    elif 'cygwin' in sys.platform:
      return OperatingSystem.CYGWIN
    return None

  @staticmethod
  def IsWindows():
    """    Returns True if the current operating system is Windows.

    Returns:
        bool: True if the current operating system is Windows, False otherwise.
    """
    return OperatingSystem.Current() is OperatingSystem.WINDOWS


class Architecture(object):
  """An enum representing the system architecture you are running on."""

  class _ARCH(object):
    """A single architecture."""

    # pylint: disable=redefined-builtin
    def __init__(self, id, name, file_name):
      self.id = id
      self.name = name
      self.file_name = file_name

    def __str__(self):
      """Return the string representation of the object's id.

      Returns:
          str: The string representation of the object's id.
      """

      return self.id

    def __eq__(self, other):
      """Compare if two objects are equal based on their id, name, and file_name
      attributes.

      Args:
          other (object): The object to compare with.

      Returns:
          bool: True if the objects are equal, False otherwise.
      """

      return (isinstance(other, type(self)) and
              self.id == other.id and
              self.name == other.name and
              self.file_name == other.file_name)

    def __hash__(self):
      """Return the hash value of the object based on its id, name, and file
      name.

      This method calculates the hash value by summing the hash values of the
      id, name, and file name attributes.

      Returns:
          int: The hash value of the object.
      """

      return hash(self.id) + hash(self.name) + hash(self.file_name)

    def __ne__(self, other):
      """Check if two objects are not equal.

      This method overrides the '!=' operator to check if two objects are not
      equal.

      Args:
          self: The first object to compare.
          other: The second object to compare.

      Returns:
          bool: True if the two objects are not equal, False otherwise.
      """

      return not self == other

    @classmethod
    def _CmpHelper(cls, x, y):
      """      Just a helper equivalent to the cmp() function in Python 2.

      Args:
          cls: The class instance.
          x: The first value for comparison.
          y: The second value for comparison.

      Returns:
          int: Returns -1 if x < y, 0 if x == y, and 1 if x > y.
      """
      return (x > y) - (x < y)

    def __lt__(self, other):
      """Compares the current object with another object based on id, name, and
      file_name attributes.

      Args:
          self (object): The current object.
          other (object): The other object to compare with.

      Returns:
          bool: True if the current object is less than the other object, False
              otherwise.
      """

      return self._CmpHelper(
          (self.id, self.name, self.file_name),
          (other.id, other.name, other.file_name)) < 0

    def __gt__(self, other):
      """Compares the current object with another object based on the id, name,
      and file_name attributes.

      Args:
          self: An instance of the class.
          other: Another instance of the class to compare with.

      Returns:
          bool: True if the current object is greater than the other object, False
              otherwise.
      """

      return self._CmpHelper(
          (self.id, self.name, self.file_name),
          (other.id, other.name, other.file_name)) > 0

    def __le__(self, other):
      """Returns True if the object is less than or equal to the 'other' object.

      This method is used to implement the less than or equal to comparison
      operation.

      Args:
          self: The object on which the method is called.
          other: The object to compare with.

      Returns:
          bool: True if the object is less than or equal to 'other', False otherwise.
      """

      return not self.__gt__(other)

    def __ge__(self, other):
      """Special method to implement the greater than or equal to (>=) comparison
      for custom objects.

      Args:
          self: The instance of the custom object.
          other: The object to compare against.

      Returns:
          bool: True if self is greater than or equal to other, False otherwise.
      """

      return not self.__lt__(other)

  x86 = _ARCH('x86', 'x86', 'x86')
  x86_64 = _ARCH('x86_64', 'x86_64', 'x86_64')
  ppc = _ARCH('PPC', 'PPC', 'ppc')
  arm = _ARCH('arm', 'arm', 'arm')
  _ALL = [x86, x86_64, ppc, arm]

  # Possible values for `uname -m` and what arch they map to.
  # Examples of possible values: https://en.wikipedia.org/wiki/Uname
  _MACHINE_TO_ARCHITECTURE = {
      'amd64': x86_64, 'x86_64': x86_64, 'i686-64': x86_64,
      'i386': x86, 'i686': x86, 'x86': x86,
      'ia64': x86,  # Itanium is different x64 arch, treat it as the common x86.
      'powerpc': ppc, 'power macintosh': ppc, 'ppc64': ppc,
      'armv6': arm, 'armv6l': arm, 'arm64': arm, 'armv7': arm, 'armv7l': arm}

  @staticmethod
  def AllValues():
    """    Gets all possible enum values.

    Returns:
        list: All the enum values.
    """
    return list(Architecture._ALL)

  @staticmethod
  def FromId(architecture_id, error_on_unknown=True):
    """    Gets the enum corresponding to the given architecture id.

    This function takes an architecture id as input and returns the
    corresponding ArchitectureTuple.
    """
    if not architecture_id:
      return None
    for arch in Architecture._ALL:
      if arch.id == architecture_id:
        return arch
    if error_on_unknown:
      raise InvalidEnumValue(architecture_id, 'Architecture',
                             [value.id for value in Architecture._ALL])
    return None

  @staticmethod
  def Current():
    """    Determines the current system architecture.

    Returns:
        ArchitectureTuple: One of the Architecture constants or None if it cannot be determined.
    """
    return Architecture._MACHINE_TO_ARCHITECTURE.get(platform.machine().lower())


class Platform(object):
  """Holds an operating system and architecture."""

  def __init__(self, operating_system, architecture):
    """Constructs a new platform.

    Args:
      operating_system: OperatingSystem, The OS
      architecture: Architecture, The machine architecture.
    """
    self.operating_system = operating_system
    self.architecture = architecture

  def __str__(self):
    """Return a string representation of the object.

    Returns a formatted string containing the operating system and
    architecture of the object.

    Returns:
        str: A string representation of the object in the format 'operating_system-
            architecture'.
    """

    return '{}-{}'.format(self.operating_system, self.architecture)

  @staticmethod
  def Current(os_override=None, arch_override=None):
    """    Determines the current platform you are running on.

    Args:
        os_override (OperatingSystem): A value to use instead of the current operating system.
        arch_override (Architecture): A value to use instead of the current architecture.

    Returns:
        Platform: The platform tuple of operating system and architecture. Either can be
            None if it could not be determined.
    """
    return Platform(
        os_override if os_override else OperatingSystem.Current(),
        arch_override if arch_override else Architecture.Current())

  def UserAgentFragment(self):
    """    Generates the fragment of the User-Agent that represents the OS.

    This function generates a fragment of the User-Agent string based on the
    operating system. It provides examples of the generated fragments for
    different operating systems.

    Returns:
        str: The fragment of the User-Agent string.

    Examples:
        (Linux 3.2.5-gg1236)
        - (Windows NT 6.1.7601)
        - (Macintosh; PPC Mac OS X 12.4.0)
        - (Macintosh; Intel Mac OS X 12.4.0)
    """
    # Below, there are examples of the value of platform.uname() per platform.
    # platform.release() is uname[2], platform.version() is uname[3].
    if self.operating_system == OperatingSystem.LINUX:
      # ('Linux', '<hostname goes here>', '3.2.5-gg1236',
      # '#1 SMP Tue May 21 02:35:06 PDT 2013', 'x86_64', 'x86_64')
      return '({name} {version})'.format(
          name=self.operating_system.name, version=platform.release())
    elif self.operating_system == OperatingSystem.WINDOWS:
      # ('Windows', '<hostname goes here>', '7', '6.1.7601', 'AMD64',
      # 'Intel64 Family 6 Model 45 Stepping 7, GenuineIntel')
      return '({name} NT {version})'.format(
          name=self.operating_system.name, version=platform.version())
    elif self.operating_system == OperatingSystem.MACOSX:
      # ('Darwin', '<hostname goes here>', '12.4.0',
      # 'Darwin Kernel Version 12.4.0: Wed May  1 17:57:12 PDT 2013;
      # root:xnu-2050.24.15~1/RELEASE_X86_64', 'x86_64', 'i386')
      format_string = '(Macintosh; {name} Mac OS X {version})'
      arch_string = (self.architecture.name
                     if self.architecture == Architecture.ppc else 'Intel')
      return format_string.format(
          name=arch_string, version=platform.release())
    else:
      return '()'

  def AsyncPopenArgs(self):
    """    Returns the arguments for spawning an asynchronous process using Popen
    on this OS.

    This method determines the arguments required to spawn an asynchronous
    process using Popen based on the operating system. For Windows, it
    ensures that the main process does not wait for the new process by
    detaching it. It also closes all file descriptors to prevent inadvertent
    waiting for the new process output. On Unix-like systems, it sets up a
    new session with the new process as the group leader to prevent
    termination if the parent process is killed.

    Returns:
        dict: The arguments for spawning an asynchronous process using Popen on this
            OS.
    """
    args = {}
    if self.operating_system == OperatingSystem.WINDOWS:
      args['close_fds'] = True  # This is enough to close _all_ FDs on windows.
      detached_process = 0x00000008
      create_new_process_group = 0x00000200
      # 0x008 | 0x200 == 0x208
      args['creationflags'] = detached_process | create_new_process_group
    else:
      # Killing a group leader kills the whole group.
      # Create a new session with the new process the group leader.
      args['preexec_fn'] = os.setsid
      args['close_fds'] = True  # This closes all FDs _except_ 0, 1, 2 on *nix.
      args['stdin'] = subprocess.PIPE
      args['stdout'] = subprocess.PIPE
      args['stderr'] = subprocess.PIPE
    return args


class PythonVersion(object):
  """Class to validate the Python version we are using.

  The Cloud SDK officially supports Python 2.7.

  However, many commands do work with Python 2.6, so we don't error out when
  users are using this (we consider it sometimes "compatible" but not
  "supported").
  """

  # See class docstring for descriptions of what these mean
  MIN_REQUIRED_PY2_VERSION = (2, 6)
  MIN_SUPPORTED_PY2_VERSION = (2, 7)
  MIN_SUPPORTED_PY3_VERSION = (3, 4)
  ENV_VAR_MESSAGE = """\

If you have a compatible Python interpreter installed, you can use it by setting
the CLOUDSDK_PYTHON environment variable to point to it.

"""

  def __init__(self, version=None):
    if version:
      self.version = version
    elif hasattr(sys, 'version_info'):
      self.version = sys.version_info[:2]
    else:
      self.version = None

  def SupportedVersionMessage(self, allow_py3):
    """Generate a message indicating the supported Python versions.

    This function generates a message based on the allowed Python versions.

    Args:
        allow_py3 (bool): A boolean indicating whether Python 3 is allowed.

    Returns:
        str: A message indicating the supported Python versions.
    """

    if allow_py3:
      return 'Please use Python version {0}.{1}.x or {2}.{3} and up.'.format(
          PythonVersion.MIN_SUPPORTED_PY2_VERSION[0],
          PythonVersion.MIN_SUPPORTED_PY2_VERSION[1],
          PythonVersion.MIN_SUPPORTED_PY3_VERSION[0],
          PythonVersion.MIN_SUPPORTED_PY3_VERSION[1])
    else:
      return 'Please use Python version {0}.{1}.x.'.format(
          PythonVersion.MIN_SUPPORTED_PY2_VERSION[0],
          PythonVersion.MIN_SUPPORTED_PY2_VERSION[1])

  def IsCompatible(self, allow_py3=False, raise_exception=False):
    """    Ensure that the Python version is compatible for the Google Cloud SDK.

    This method checks if the current Python version is compatible with the
    Google Cloud SDK. It prints an error message if the version is not
    compatible.
    """
    error = None
    if not self.version:
      # We don't know the version, not a good sign.
      error = ('ERROR: Your current version of Python is not compatible with '
               'the Google Cloud SDK. {0}\n'
               .format(self.SupportedVersionMessage(allow_py3)))
    else:
      if self.version[0] < 3:
        # Python 2 Mode
        if self.version < PythonVersion.MIN_REQUIRED_PY2_VERSION:
          error = ('ERROR: Python {0}.{1} is not compatible with the Google '
                   'Cloud SDK. {2}\n'
                   .format(self.version[0], self.version[1],
                           self.SupportedVersionMessage(allow_py3)))
      else:
        # Python 3 Mode
        if not allow_py3:
          error = ('ERROR: Python 3 and later is not compatible with the '
                   'Google Cloud SDK. {0}\n'
                   .format(self.SupportedVersionMessage(allow_py3)))
        elif self.version < PythonVersion.MIN_SUPPORTED_PY3_VERSION:
          error = ('ERROR: Python {0}.{1} is not compatible with the Google '
                   'Cloud SDK. {2}\n'
                   .format(self.version[0], self.version[1],
                           self.SupportedVersionMessage(allow_py3)))

    if error:
      if raise_exception:
        raise Error(error)
      sys.stderr.write(error)
      sys.stderr.write(PythonVersion.ENV_VAR_MESSAGE)
      return False

    # Warn that 2.6 might not work.
    if (self.version >= self.MIN_REQUIRED_PY2_VERSION and
        self.version < self.MIN_SUPPORTED_PY2_VERSION):
      sys.stderr.write("""\
WARNING:  Python 2.6.x is no longer officially supported by the Google Cloud SDK
and may not function correctly.  {0}
{1}""".format(self.SupportedVersionMessage(allow_py3),
              PythonVersion.ENV_VAR_MESSAGE))

    return True
