# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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

"""OS specific console_attr helper functions."""

import os
import sys

from fire.console import encoding


def GetTermSize():
  """  Gets the terminal x and y dimensions in characters.

  _GetTermSize*() helper functions taken from:
  http://stackoverflow.com/questions/263890/

  Returns:
      tuple: A tuple containing the terminal x and y dimensions.
          The first element represents the number of columns, and the second
          element represents the number of lines.
  """
  xy = None
  # Believe the first helper that doesn't bail.
  for get_terminal_size in (_GetTermSizePosix,
                            _GetTermSizeWindows,
                            _GetTermSizeEnvironment,
                            _GetTermSizeTput):
    try:
      xy = get_terminal_size()
      if xy:
        break
    except:  # pylint: disable=bare-except
      pass
  return xy or (80, 24)


def _GetTermSizePosix():
  """  Returns the Posix terminal x and y dimensions.

  This function retrieves the x and y dimensions of the Posix terminal by
  utilizing various system libraries and methods.

  Returns:
      tuple: A tuple containing the x and y dimensions of the Posix terminal.
          Returns None if the dimensions cannot be retrieved.
  """
  # pylint: disable=g-import-not-at-top
  import fcntl
  # pylint: disable=g-import-not-at-top
  import struct
  # pylint: disable=g-import-not-at-top
  import termios

  def _GetXY(fd):
    """    Returns the terminal (x,y) size for a given file descriptor.

    This function takes a file descriptor as input and retrieves the
    terminal size (x, y) associated with it.

    Args:
        fd: int, The file descriptor of the terminal.

    Returns:
        tuple or None: A tuple containing the terminal size in the format (x,
            y). Returns None on error.
    """
    try:
      # This magic incantation converts a struct from ioctl(2) containing two
      # binary shorts to a (rows, columns) int tuple.
      rc = struct.unpack(b'hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, 'junk'))
      return (rc[1], rc[0]) if rc else None
    except:  # pylint: disable=bare-except
      return None

  xy = _GetXY(0) or _GetXY(1) or _GetXY(2)
  if not xy:
    fd = None
    try:
      fd = os.open(os.ctermid(), os.O_RDONLY)
      xy = _GetXY(fd)
    except:  # pylint: disable=bare-except
      xy = None
    finally:
      if fd is not None:
        os.close(fd)
  return xy


def _GetTermSizeWindows():
  """  Returns the Windows terminal x and y dimensions.

  This function retrieves the dimensions of the Windows terminal by using
  ctypes and Windows API functions.

  Returns:
      tuple: A tuple containing the x and y dimensions of the Windows terminal.
  """
  # pylint:disable=g-import-not-at-top
  import struct
  # pylint: disable=g-import-not-at-top
  from ctypes import create_string_buffer
  # pylint:disable=g-import-not-at-top
  from ctypes import windll

  # stdin handle is -10
  # stdout handle is -11
  # stderr handle is -12

  h = windll.kernel32.GetStdHandle(-12)
  csbi = create_string_buffer(22)
  if not windll.kernel32.GetConsoleScreenBufferInfo(h, csbi):
    return None
  (unused_bufx, unused_bufy, unused_curx, unused_cury, unused_wattr,
   left, top, right, bottom,
   unused_maxx, unused_maxy) = struct.unpack(b'hhhhHhhhhhh', csbi.raw)
  x = right - left + 1
  y = bottom - top + 1
  return (x, y)


def _GetTermSizeEnvironment():
  """  Returns the terminal x and y dimensions from the environment.

  Returns:
      tuple: A tuple containing the x and y dimensions of the terminal.
  """
  return (int(os.environ['COLUMNS']), int(os.environ['LINES']))


def _GetTermSizeTput():
  """  Returns the terminal x and y dimensions using tput(1).

  This function executes the 'tput cols' and 'tput lines' commands to get
  the number of columns and rows in the terminal.

  Returns:
      tuple: A tuple containing the number of columns and rows in the terminal.
  """
  import subprocess  # pylint: disable=g-import-not-at-top
  output = encoding.Decode(subprocess.check_output(['tput', 'cols'],
                                                   stderr=subprocess.STDOUT))
  cols = int(output)
  output = encoding.Decode(subprocess.check_output(['tput', 'lines'],
                                                   stderr=subprocess.STDOUT))
  rows = int(output)
  return (cols, rows)


_ANSI_CSI = '\x1b'  # ANSI control sequence indicator (ESC)
_CONTROL_D = '\x04'  # unix EOF (^D)
_CONTROL_Z = '\x1a'  # Windows EOF (^Z)
_WINDOWS_CSI_1 = '\x00'  # Windows control sequence indicator #1
_WINDOWS_CSI_2 = '\xe0'  # Windows control sequence indicator #2


def GetRawKeyFunction():
  """  Returns a function that reads one keypress from stdin with no echo.

  This function tries to obtain a function that reads one keypress from
  stdin with no echo. It first tries to get the function from the
  platform-specific implementations for POSIX and Windows. If both
  platform-specific implementations fail, it returns a lambda function
  that always returns None.

  Returns:
      function: A function that reads one keypress from stdin with no echo or a function
      that always returns None if stdin does not support it.
  """
  # Believe the first helper that doesn't bail.
  for get_raw_key_function in (_GetRawKeyFunctionPosix,
                               _GetRawKeyFunctionWindows):
    try:
      return get_raw_key_function()
    except:  # pylint: disable=bare-except
      pass
  return lambda: None


def _GetRawKeyFunctionPosix():
  """  _GetRawKeyFunction helper using Posix APIs.

  This function is a helper function that utilizes Posix APIs to read and
  return one keypress from stdin without echoing the input.

  Returns:
      str: The key name, None for EOF, <*> for function keys, otherwise a
          character.
  """
  # pylint: disable=g-import-not-at-top
  import tty
  # pylint: disable=g-import-not-at-top
  import termios

  def _GetRawKeyPosix():
    """    Reads and returns one keypress from stdin, no echo, using Posix APIs.

    Returns:
        The key name, None for EOF, <*> for function keys, otherwise a
            character.
    """
    ansi_to_key = {
        'A': '<UP-ARROW>',
        'B': '<DOWN-ARROW>',
        'D': '<LEFT-ARROW>',
        'C': '<RIGHT-ARROW>',
        '5': '<PAGE-UP>',
        '6': '<PAGE-DOWN>',
        'H': '<HOME>',
        'F': '<END>',
        'M': '<DOWN-ARROW>',
        'S': '<PAGE-UP>',
        'T': '<PAGE-DOWN>',
    }

    # Flush pending output. sys.stdin.read() would do this, but it's explicitly
    # bypassed in _GetKeyChar().
    sys.stdout.flush()

    fd = sys.stdin.fileno()

    def _GetKeyChar():
      """Get a single character key from the input.

      Reads a single character key from the file descriptor and decodes it
      using the system encoding.

      Returns:
          str: A single character key.
      """

      return encoding.Decode(os.read(fd, 1))

    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(fd)
      c = _GetKeyChar()
      if c == _ANSI_CSI:
        c = _GetKeyChar()
        while True:
          if c == _ANSI_CSI:
            return c
          if c.isalpha():
            break
          prev_c = c
          c = _GetKeyChar()
          if c == '~':
            c = prev_c
            break
        return ansi_to_key.get(c, '')
    except:  # pylint:disable=bare-except
      c = None
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None if c in (_CONTROL_D, _CONTROL_Z) else c

  return _GetRawKeyPosix


def _GetRawKeyFunctionWindows():
  """  _GetRawKeyFunction helper using Windows APIs.

  This function defines a helper function that reads and returns one
  keypress from stdin without echo, using Windows APIs.

  Returns:
      str: The key name, None for EOF, <*> for function keys, otherwise a
          character.
  """
  # pylint: disable=g-import-not-at-top
  import msvcrt

  def _GetRawKeyWindows():
    """    Reads and returns one keypress from stdin, no echo, using Windows APIs.

    Returns:
        The key name, None for EOF, <*> for function keys, otherwise a
            character.
    """
    windows_to_key = {
        'H': '<UP-ARROW>',
        'P': '<DOWN-ARROW>',
        'K': '<LEFT-ARROW>',
        'M': '<RIGHT-ARROW>',
        'I': '<PAGE-UP>',
        'Q': '<PAGE-DOWN>',
        'G': '<HOME>',
        'O': '<END>',
    }

    # Flush pending output. sys.stdin.read() would do this it's explicitly
    # bypassed in _GetKeyChar().
    sys.stdout.flush()

    def _GetKeyChar():
      """Get a single character key pressed by the user.

      This function retrieves a single character key pressed by the user using
      msvcrt.getch() function.

      Returns:
          str: A single character key pressed by the user.
      """

      return encoding.Decode(msvcrt.getch())

    c = _GetKeyChar()
    # Special function key is a two character sequence; return the second char.
    if c in (_WINDOWS_CSI_1, _WINDOWS_CSI_2):
      return windows_to_key.get(_GetKeyChar(), '')
    return None if c in (_CONTROL_D, _CONTROL_Z) else c

  return _GetRawKeyWindows
