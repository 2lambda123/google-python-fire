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

"""Docstring parsing module for Python Fire.

The following features of docstrings are not supported.
TODO(dbieber): Support these features.
- numpy docstrings may begin with the function signature.
- whitespace may be important for proper structuring of a docstring
- I've seen `argname` (with single backticks) as a style of documenting
  arguments. The `argname` appears on one line, and the description on the next.
- .. Sphinx directives such as .. note:: are not understood.
- After a section ends, future contents may be included in the section. E.g.
  :returns: This is what is returned.
  Example: An example goes here.
- @param is sometimes used.  E.g.
  @param argname (type) Description
  @return (type) Description
- The true signature of a function is not used by the docstring parser. It could
  be useful for determining whether something is a section header or an argument
  for example.
- This example confuses types as part of the docstrings.
  Parameters
  argname : argtype
  Arg description
- If there's no blank line after the summary, the description will be slurped
  up into the summary.
- "Examples" should be its own section type. aka "Usage".
- "Notes" should be a section type.
- Some people put parenthesis around their types in RST format, e.g.
  :param (type) paramname:
- :rtype: directive (return type)
- Also ":rtype str" with no closing ":" has come up.
- Return types are not supported.
- "# Returns" as a section title style
- ":raises ExceptionType: Description" ignores the ExceptionType currently.
- "Defaults to X" occurs sometimes.
- "True | False" indicates bool type.
"""

import collections
import enum
import re
import textwrap


class DocstringInfo(
    collections.namedtuple(
        'DocstringInfo',
        ('summary', 'description', 'args', 'returns', 'yields', 'raises'))):
  pass
DocstringInfo.__new__.__defaults__ = (None,) * len(DocstringInfo._fields)


class ArgInfo(
    collections.namedtuple(
        'ArgInfo',
        ('name', 'type', 'description'))):
  pass
ArgInfo.__new__.__defaults__ = (None,) * len(ArgInfo._fields)


class KwargInfo(ArgInfo):
  pass
KwargInfo.__new__.__defaults__ = (None,) * len(KwargInfo._fields)


class Namespace(dict):
  """A dict with attribute (dot-notation) access enabled."""

  def __getattr__(self, key):
    """Return the value associated with the given key. If the key does not
    exist in the namespace,
    a new Namespace object is created and associated with the key before
    returning it.

    Args:
        key (str): The key to retrieve the value for.

    Returns:
        Namespace: The value associated with the key, or a new Namespace object if the key
            does not exist.
    """

    if key not in self:
      self[key] = Namespace()
    return self[key]

  def __setattr__(self, key, value):
    """Set the value of an attribute in the object's dictionary.

    This method allows setting the value of an attribute in the object's
    dictionary directly.

    Args:
        key (str): The key to be set in the object's dictionary.
        value: The value to be associated with the key.
    """

    self[key] = value

  def __delattr__(self, key):
    """Delete the attribute with the specified key from the object.

    Args:
        key (str): The key of the attribute to be deleted.
    """

    if key in self:
      del self[key]


class Sections(enum.Enum):
  ARGS = 0
  RETURNS = 1
  YIELDS = 2
  RAISES = 3
  TYPE = 4


class Formats(enum.Enum):
  GOOGLE = 0
  NUMPY = 1
  RST = 2


SECTION_TITLES = {
    Sections.ARGS: ('argument', 'arg', 'parameter', 'param', 'key'),
    Sections.RETURNS: ('return',),
    Sections.YIELDS: ('yield',),
    Sections.RAISES: ('raise', 'except', 'exception', 'throw', 'error', 'warn'),
    Sections.TYPE: ('type',),  # rst-only
}


def parse(docstring):
  """  Returns DocstringInfo about the given docstring.

  This parser aims to parse Google, numpy, and rst formatted docstrings.
  These are the three most common docstring styles at the time of this
  writing.  This parser aims to be permissive, working even when the
  docstring deviates from the strict recommendations of these styles.
  This parser does not aim to fully extract all structured information
  from a docstring, since there are simply too many ways to structure
  information in a docstring. Sometimes content will remain as
  unstructured text and simply gets included in the description.  The
  Google docstring style guide is available at:
  https://github.com/google/styleguide/blob/gh-pages/pyguide.md  The numpy
  docstring style guide is available at:
  https://numpydoc.readthedocs.io/en/latest/format.html  Information about
  the rST docstring format is available at:
  https://www.python.org/dev/peps/pep-0287/ The full set of directives
  such as param and type for rST docstrings are at: http://www.sphinx-
  doc.org/en/master/usage/restructuredtext/domains.html  Note: This
  function does not claim to handle all docstrings well. A list of
  limitations is available at the top of the file. It does aim to run
  without crashing in O(n) time on all strings on length n. If you find a
  string that causes this to crash or run unacceptably slowly, please
  consider submitting a pull request.

  Args:
      docstring (str): The docstring to parse.

  Returns:
      DocstringInfo: A DocstringInfo containing information about the docstring.
  """
  if docstring is None:
    return DocstringInfo()

  lines = docstring.strip().split('\n')
  lines_len = len(lines)
  state = Namespace()  # TODO(dbieber): Switch to an explicit class.

  # Variables in state include:
  state.section.title = None
  state.section.indentation = None
  state.section.line1_indentation = None
  state.section.format = None
  state.summary.permitted = True
  state.summary.lines = []
  state.description.lines = []
  state.args = []
  state.kwargs = []
  state.current_arg = None
  state.returns.lines = []
  state.yields.lines = []
  state.raises.lines = []

  for index, line in enumerate(lines):
    has_next = index + 1 < lines_len
    previous_line = lines[index - 1] if index > 0 else None
    next_line = lines[index + 1] if has_next else None
    line_info = _create_line_info(line, next_line, previous_line)
    _consume_line(line_info, state)

  summary = ' '.join(state.summary.lines) if state.summary.lines else None
  state.description.lines = _strip_blank_lines(state.description.lines)
  description = textwrap.dedent('\n'.join(state.description.lines))
  if not description:
    description = None
  returns = _join_lines(state.returns.lines)
  yields = _join_lines(state.yields.lines)
  raises = _join_lines(state.raises.lines)

  args = [ArgInfo(
      name=arg.name, type=_cast_to_known_type(_join_lines(arg.type.lines)),
      description=_join_lines(arg.description.lines)) for arg in state.args]

  args.extend([KwargInfo(
      name=arg.name, type=_cast_to_known_type(_join_lines(arg.type.lines)),
      description=_join_lines(arg.description.lines)) for arg in state.kwargs])

  return DocstringInfo(
      summary=summary,
      description=description,
      args=args or None,
      returns=returns,
      raises=raises,
      yields=yields,
  )


def _strip_blank_lines(lines):
  """  Removes lines containing only blank characters before and after the
  text.

  It takes a list of lines as input and removes any leading or trailing
  blank lines.

  Args:
      lines (list): A list of lines.

  Returns:
      list: A list of lines without trailing or leading blank lines.
  """
  # Find the first non-blank line.
  start = 0
  num_lines = len(lines)
  while lines and start < num_lines and _is_blank(lines[start]):
    start += 1

  lines = lines[start:]

  # Remove trailing blank lines.
  while lines and _is_blank(lines[-1]):
    lines.pop()

  return lines


def _is_blank(line):
  """Check if a given line is blank or contains only whitespace characters.

  Args:
      line (str): A string representing a line of text.

  Returns:
      bool: True if the line is blank or contains only whitespace characters, False
          otherwise.
  """

  return not line or line.isspace()


def _join_lines(lines):
  """  Joins lines with the appropriate connective whitespace.

  This function takes a list of lines and joins them together with a
  single space between consecutive lines, unless there is a blank line, in
  which case a full blank line is included.

  Args:
      lines (list): A list of lines to join.

  Returns:
      str: The lines joined together.
  """
  # TODO(dbieber): Add parameters for variations in whitespace handling.
  if not lines:
    return None

  started = False
  group_texts = []  # Full text of each section.
  group_lines = []  # Lines within the current section.
  for line in lines:
    stripped_line = line.strip()
    if stripped_line:
      started = True
      group_lines.append(stripped_line)
    else:
      if started:
        group_text = ' '.join(group_lines)
        group_texts.append(group_text)
        group_lines = []

  if group_lines:  # Process the final group.
    group_text = ' '.join(group_lines)
    group_texts.append(group_text)

  return '\n\n'.join(group_texts)


def _get_or_create_arg_by_name(state, name, is_kwarg=False):
  """  Gets or creates a new Arg.

  These Arg objects (Namespaces) are turned into the ArgInfo namedtuples
  returned by parse. Each Arg object is used to collect the name, type,
  and description of a single argument to the docstring's function.

  Args:
      state (object): The state of the parser.
      name (str): The name of the arg to create.
      is_kwarg (bool?): A boolean representing whether the argument is a keyword arg. Defaults
          to False.

  Returns:
      object: The new Arg.
  """
  for arg in state.args + state.kwargs:
    if arg.name == name:
      return arg
  arg = Namespace()  # TODO(dbieber): Switch to an explicit class.
  arg.name = name
  arg.type.lines = []
  arg.description.lines = []
  if is_kwarg:
    state.kwargs.append(arg)
  else:
    state.args.append(arg)
  return arg


def _is_arg_name(name):
  """  Returns whether name is a valid arg name.

  This function checks if the input name is a valid argument name by
  ensuring it follows the pattern of a letter or underscore followed by
  zero or more letters, numbers, or underscores. This is important to
  prevent multiple words from being misinterpreted as an argument name.

  Args:
      name (str): The name of the potential arg.

  Returns:
      bool: True if name looks like an arg name, False otherwise.
  """
  name = name.strip()
  # arg_pattern is a letter or underscore followed by
  # zero or more letters, numbers, or underscores.
  arg_pattern = r'^[a-zA-Z_]\w*$'
  re.match(arg_pattern, name)
  return re.match(arg_pattern, name) is not None


def _as_arg_name_and_type(text):
  """  Returns text as a name and type, if text looks like an arg name and
  type.

  This function takes a text input and checks if it resembles an argument
  name and type. If the text matches the format 'name (type)', it extracts
  and returns the name and type.

  Args:
      text (str): The text to be checked for arg name and type.

  Returns:
      tuple: A tuple containing the arg name and type if found, otherwise None.
  """
  tokens = text.split()
  if len(tokens) < 2:
    return None
  if _is_arg_name(tokens[0]):
    type_token = ' '.join(tokens[1:])
    type_token = type_token.lstrip('{([').rstrip('])}')
    return tokens[0], type_token
  else:
    return None


def _as_arg_names(names_str):
  """  Converts names_str to a list of argument names.

  This function takes a string containing multiple space or comma
  separated argument names and converts it into a list of argument names.

  Args:
      names_str (str): A string with multiple space or comma separated argument names.

  Returns:
      list: A list of argument names, or None if names_str doesn't look like a list
          of argument names.
  """
  names = re.split(',| ', names_str)
  names = [name.strip() for name in names if name.strip()]
  for name in names:
    if not _is_arg_name(name):
      return None
  if not names:
    return None
  return names


def _cast_to_known_type(name):
  """  Canonicalizes a string representing a type if possible.

  This function takes a string representing a type and removes any
  trailing period to provide a canonicalized version of the type string.
  It supports additional canonicalization in the future.

  Args:
      name (str): A string representing a type, or None.

  Returns:
      str: A canonicalized version of the type string.
  """
  if name is None:
    return None
  return name.rstrip('.')


def _consume_google_args_line(line_info, state):
  """  Consume a single line from a Google args section.

  This function processes a single line from a Google-style args section.
  It splits the line into the argument name and description, and updates
  the state accordingly. If the line contains an argument name, it creates
  or retrieves the argument object and updates its description. If the
  line contains argument type information, it updates the argument's type
  information. If neither of these conditions are met, it appends the line
  to the current argument's description.

  Args:
      line_info (object): Information about the current line being processed.
      state (object): The current state of the processing.
  """
  split_line = line_info.remaining.split(':', 1)
  if len(split_line) > 1:
    first, second = split_line  # first is either the "arg" or "arg (type)"
    if _is_arg_name(first.strip()):
      arg = _get_or_create_arg_by_name(state, first.strip())
      arg.description.lines.append(second.strip())
      state.current_arg = arg
    else:
      arg_name_and_type = _as_arg_name_and_type(first)
      if arg_name_and_type:
        arg_name, type_str = arg_name_and_type
        arg = _get_or_create_arg_by_name(state, arg_name)
        arg.type.lines.append(type_str)
        arg.description.lines.append(second.strip())
        state.current_arg = arg
      else:
        if state.current_arg:
          state.current_arg.description.lines.append(split_line[0])
  else:
    if state.current_arg:
      state.current_arg.description.lines.append(split_line[0])


def _consume_line(line_info, state):
  """  Consumes one line of text, updating the state accordingly.

  When _consume_line is called, part of the line may already have been
  processed for header information.

  Args:
      line_info (tuple): Information about the current and next line of the docstring.
      state (State): The state of the docstring parser.
  """
  _update_section_state(line_info, state)

  if state.section.title is None:
    if state.summary.permitted:
      if line_info.remaining:
        state.summary.lines.append(line_info.remaining)
      elif state.summary.lines:
        state.summary.permitted = False
    else:
      # We're past the end of the summary.
      # Additions now contribute to the description.
      state.description.lines.append(line_info.remaining_raw)
  else:
    state.summary.permitted = False

  if state.section.new and state.section.format == Formats.RST:
    # The current line starts with an RST directive, e.g. ":param arg:".
    directive = _get_directive(line_info)
    directive_tokens = directive.split()  # pytype: disable=attribute-error
    if state.section.title == Sections.ARGS:
      name = directive_tokens[-1]
      arg = _get_or_create_arg_by_name(
          state,
          name,
          is_kwarg=directive_tokens[0] == 'key'
      )
      if len(directive_tokens) == 3:
        # A param directive of the form ":param type arg:".
        arg.type.lines.append(directive_tokens[1])
      state.current_arg = arg
    elif state.section.title == Sections.TYPE:
      name = directive_tokens[-1]
      arg = _get_or_create_arg_by_name(state, name)
      state.current_arg = arg

  if (state.section.format == Formats.NUMPY and
      _line_is_hyphens(line_info.remaining)):
    # Skip this all-hyphens line, which is part of the numpy section header.
    return

  if state.section.title == Sections.ARGS:
    if state.section.format == Formats.GOOGLE:
      _consume_google_args_line(line_info, state)
    elif state.section.format == Formats.RST:
      state.current_arg.description.lines.append(line_info.remaining.strip())
    elif state.section.format == Formats.NUMPY:
      line_stripped = line_info.remaining.strip()
      if _is_arg_name(line_stripped):
        # Token on its own line can either be the last word of the description
        # of the previous arg, or a new arg. TODO: Whitespace can distinguish.
        arg = _get_or_create_arg_by_name(state, line_stripped)
        state.current_arg = arg
      elif _line_is_numpy_parameter_type(line_info):
        possible_args, type_data = line_stripped.split(':', 1)
        arg_names = _as_arg_names(possible_args)  # re.split(' |,', s)
        if arg_names:
          for arg_name in arg_names:
            arg = _get_or_create_arg_by_name(state, arg_name)
            arg.type.lines.append(type_data)
            state.current_arg = arg  # TODO(dbieber): Multiple current args.
        else:  # Just an ordinary line.
          if state.current_arg:
            state.current_arg.description.lines.append(
                line_info.remaining.strip())
          else:
            # TODO(dbieber): If not a blank line, add it to the description.
            pass
      else:  # Just an ordinary line.
        if state.current_arg:
          state.current_arg.description.lines.append(
              line_info.remaining.strip())
        else:
          # TODO(dbieber): If not a blank line, add it to the description.
          pass

  elif state.section.title == Sections.RETURNS:
    state.returns.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.YIELDS:
    state.yields.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.RAISES:
    state.raises.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.TYPE:
    if state.section.format == Formats.RST:
      assert state.current_arg is not None
      state.current_arg.type.lines.append(line_info.remaining.strip())
    else:
      pass


def _create_line_info(line, next_line, previous_line):
  """  Returns information about the current line and surrounding lines.

  It creates a Namespace object to store information about the current
  line and its surrounding lines. The function extracts details such as
  the stripped version of the line, remaining raw line, remaining stripped
  line, indentation of the current line, next line, and previous line.

  Args:
      line (str): The current line of text.
      next_line (str): The next line of text.
      previous_line (str): The previous line of text.

  Returns:
      Namespace: An object containing information about the current line and surrounding
          lines.
  """
  line_info = Namespace()  # TODO(dbieber): Switch to an explicit class.
  line_info.line = line
  line_info.stripped = line.strip()
  line_info.remaining_raw = line_info.line
  line_info.remaining = line_info.stripped
  line_info.indentation = len(line) - len(line.lstrip())
  # TODO(dbieber): If next_line is blank, use the next non-blank line.
  line_info.next.line = next_line
  next_line_exists = next_line is not None
  line_info.next.stripped = next_line.strip() if next_line_exists else None
  line_info.next.indentation = (
      len(next_line) - len(next_line.lstrip()) if next_line_exists else None)
  line_info.previous.line = previous_line
  previous_line_exists = previous_line is not None
  line_info.previous.indentation = (
      len(previous_line) -
      len(previous_line.lstrip()) if previous_line_exists else None)
  # Note: This counts all whitespace equally.
  return line_info


def _update_section_state(line_info, state):
  """  Uses line_info to determine the current section of the docstring.

  Updates state and line_info.remaining.

  Args:
      line_info (object): Information about the current line.
      state (object): The state of the parser.
  """
  section_updated = False

  google_section_permitted = _google_section_permitted(line_info, state)
  google_section = google_section_permitted and _google_section(line_info)
  if google_section:
    state.section.format = Formats.GOOGLE
    state.section.title = google_section
    line_info.remaining = _get_after_google_header(line_info)
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  rst_section = _rst_section(line_info)
  if rst_section:
    state.section.format = Formats.RST
    state.section.title = rst_section
    line_info.remaining = _get_after_directive(line_info)
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  numpy_section = _numpy_section(line_info)
  if numpy_section:
    state.section.format = Formats.NUMPY
    state.section.title = numpy_section
    line_info.remaining = ''
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  if section_updated:
    state.section.new = True
    state.section.indentation = line_info.indentation
    state.section.line1_indentation = line_info.next.indentation
  else:
    state.section.new = False


def _google_section_permitted(line_info, state):
  """  Returns whether a new google section is permitted to start here.

  This function determines whether a new Google section is allowed to
  start at the current line. It checks if a new section can begin based on
  the indentation and the state of the parser.

  Args:
      line_info (object): Information about the current line.
      state (object): The state of the parser.

  Returns:
      bool: True if a new Google section is permitted, False otherwise.
  """
  if state.section.indentation is None:  # We're not in a section yet.
    return True
  return (line_info.indentation <= state.section.indentation
          or line_info.indentation < state.section.line1_indentation)


def _matches_section_title(title, section_title):
  """  Returns whether the given title matches a specific section title.

  This function checks if the provided title matches a specific known
  section title. It converts both titles to lowercase for case-insensitive
  comparison and also handles plurals or minor typos.

  Args:
      title (str): The title to be checked for matching.
      section_title (str): A specific known section title to be compared against.

  Returns:
      bool: True if the titles match, False otherwise.
  """
  title = title.lower()
  section_title = section_title.lower()
  return section_title in (title, title[:-1])  # Supports plurals / some typos.


def _matches_section(title, section):
  """  Returns whether title is a match any known title for a specific section.

  This function checks if the given title matches any known title for a
  specific section.

  Args:
      title (str): The title to check for matching.
      section (Sections): A specific section to check all possible titles for.

  Returns:
      bool: True if the title is a match for the specified section, False otherwise.
  """
  for section_title in SECTION_TITLES[section]:
    if _matches_section_title(title, section_title):
      return True
  return False


def _section_from_possible_title(possible_title):
  """  Returns a section matched by the possible title, or None if none match.

  It iterates through the possible section titles and checks if the
  possible title matches any of them.

  Args:
      possible_title (str): A string that may be the title of a new section.

  Returns:
      Section: A Section type if one matches, or None if no section type matches.
  """
  for section in SECTION_TITLES:
    if _matches_section(possible_title, section):
      return section
  return None


def _google_section(line_info):
  """  Checks whether the current line is the start of a new Google-style
  section.

  This function checks if the current line marks the start of a new
  Google-style section. Google-style sections are structured as follows:
  Section Name:     section body goes here

  Args:
      line_info (object): Information about the current line.

  Returns:
      Section: A Section type if one matches, or None if no section type matches.
  """
  colon_index = line_info.remaining.find(':')
  possible_title = line_info.remaining[:colon_index]
  return _section_from_possible_title(possible_title)


def _get_after_google_header(line_info):
  """  Gets the remainder of the line, after a Google header.

  This function extracts and returns the part of the line that comes after
  a Google header.

  Args:
      line_info (object): An object containing information about the line.

  Returns:
      str: The part of the line after the Google header.
  """
  colon_index = line_info.remaining.find(':')
  return line_info.remaining[colon_index + 1:]


def _get_directive(line_info):
  """  Gets a directive from the start of the line.

  This function extracts a directive from the beginning of the line. It
  checks if the line starts with a colon and returns the directive
  content.

  Args:
      line_info (str): Information about the current line.

  Returns:
      str: The contents of a directive, or None if the line doesn't start with a
          directive.
  """
  if line_info.stripped.startswith(':'):
    return line_info.stripped.split(':', 2)[1]
  else:
    return None


def _get_after_directive(line_info):
  """  Gets the remainder of the line, after a directive.

  This function takes a LineInfo object as input and extracts the part of
  the line that comes after a directive. It splits the line based on ':'
  and returns the remaining part after the directive.

  Args:
      line_info (LineInfo): An object containing information about the line.

  Returns:
      str: The part of the line that comes after the directive.
  """
  sections = line_info.stripped.split(':', 2)
  if len(sections) > 2:
    return sections[-1]
  else:
    return ''


def _rst_section(line_info):
  """  Checks whether the current line is the start of a new RST-style section.

  RST uses directives to specify information. An RST directive, which we
  refer to as a section here, are surrounded with colons. For example,
  :param name:.

  Args:
      line_info (str): Information about the current line.

  Returns:
      Section: A Section type if one matches, or None if no section type matches.
  """
  directive = _get_directive(line_info)
  if directive:
    possible_title = directive.split()[0]
    return _section_from_possible_title(possible_title)
  else:
    return None


def _line_is_hyphens(line):
  """  Returns whether the line is entirely hyphens (and not blank).

  Args:
      line (str): The input line to check.

  Returns:
      bool: True if the line consists only of hyphens and is not blank, False
          otherwise.
  """
  return line and not line.strip('-')


def _numpy_section(line_info):
  """  Checks whether the current line is the start of a new numpy-style
  section.

  Numpy style sections are followed by a full line of hyphens, for
  example:  Section Name ------------ Section body goes here.

  Args:
      line_info (object): Information about the current line.

  Returns:
      object: A Section type if one matches, or None if no section type matches.
  """
  next_line_is_hyphens = _line_is_hyphens(line_info.next.stripped)
  if next_line_is_hyphens:
    possible_title = line_info.remaining
    return _section_from_possible_title(possible_title)
  else:
    return None


def _line_is_numpy_parameter_type(line_info):
  """  Returns whether the line contains a numpy style parameter type
  definition.

  This function checks if the line contains a numpy style parameter type
  definition. It looks for a line of the form: x : type It excludes false
  positives on argument descriptions containing a colon by checking the
  indentation of the line above.

  Args:
      line_info (object): Information about the current line.

  Returns:
      bool: True if the line is a numpy parameter type definition, False otherwise.
  """
  line_stripped = line_info.remaining.strip()
  if ':' in line_stripped:
    previous_indent = line_info.previous.indentation
    current_indent = line_info.indentation
    if ':' in line_info.previous.line and current_indent > previous_indent:
      # The parameter type was the previous line; this is the description.
      return False
    else:
      return True
  return False
