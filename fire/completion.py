# Copyright (C) 2017 Google Inc.
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

"""Provides tab completion functionality for CLIs built with Fire."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
from copy import copy
import inspect

from fire import inspectutils
import six


def Script(name, component, default_options=None):
  return _Script(name, _Commands(component), default_options)


def _Script(name, commands, default_options=None):
  """Returns a Bash script registering a completion function for the commands.

  Args:
    name: The first token in the commands, also the name of the command.
    commands: A list of all possible commands that tab completion can complete
        to. Each command is a list or tuple of the string tokens that make up
        that command.
    default_options: A dict of options that can be used with any command. Use
        this if there are flags that can always be appended to a command.
  Returns:
    A string which is the Bash script. Source the bash script to enable tab
    completion in Bash.
  """
  default_options = default_options or set()
  options_map = defaultdict(lambda: copy(default_options))
  for command in commands:
    start = (name + ' ' + ' '.join(command[:-1])).strip()
    completion = _FormatForCommand(command[-1])
    options_map[start].add(completion)
    options_map[start.replace('_', '-')].add(completion)

  bash_completion_template = """# bash completion support for {name}
# DO NOT EDIT.
# This script is autogenerated by fire/completion.py.

_complete-{identifier}()
{{
  local start cur opts
  COMPREPLY=()
  start="${{COMP_WORDS[@]:0:COMP_CWORD}}"
  cur="${{COMP_WORDS[COMP_CWORD]}}"

  opts="{default_options}"

{start_checks}

  COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
  return 0
}}

complete -F _complete-{identifier} {command}
"""
  start_check_template = """
  if [[ "$start" == "{start}" ]] ; then
    opts="{completions}"
  fi"""

  start_checks = '\n'.join(
      start_check_template.format(
          start=start,
          completions=' '.join(sorted(options_map[start]))
      )
      for start in options_map
  )

  return (
      bash_completion_template.format(
          name=name,
          command=name,
          start_checks=start_checks,
          default_options=' '.join(default_options),
          identifier=name.replace('/', '').replace('.', '').replace(',', '')
      )
  )


def _IncludeMember(name, verbose):
  if verbose:
    return True
  if isinstance(name, six.string_types):
    return name and name[0] != '_'
  return True  # Default to including the member


def _Members(component, verbose=False):
  """Returns a list of the members of the given component.

  If verbose is True, then members starting with _ (normally ignored) are
  included.

  Args:
    component: The component whose members to list.
    verbose: Whether to include private members.
  Returns:
    A list of tuples (member_name, member) of all members of the component.
  """
  if isinstance(component, dict):
    members = component.items()
  else:
    members = inspect.getmembers(component)

  return [
      (member_name, member)
      for member_name, member in members
      if _IncludeMember(member_name, verbose)
  ]


def _CompletionsFromArgs(fn_args):
  """Takes a list of fn args and returns a list of the fn's completion strings.

  Args:
    fn_args: A list of the args accepted by a function.
  Returns:
    A list of possible completion strings for that function.
  """
  completions = []
  for arg in fn_args:
    arg = arg.replace('_', '-')
    completions.append('--{arg}'.format(arg=arg))
  return completions


def Completions(component, verbose=False):
  """Gives possible Fire command completions for the component.

  A completion is a string that can be appended to a command to continue that
  command. These are used for TAB-completions in Bash for Fire CLIs.

  Args:
    component: The component whose completions to list.
    verbose: Whether to include all completions, even private members.
  Returns:
    A list of completions for a command that would so far return the component.
  """
  if inspect.isroutine(component) or inspect.isclass(component):
    spec = inspectutils.GetFullArgSpec(component)
    return _CompletionsFromArgs(spec.args + spec.kwonlyargs)

  elif isinstance(component, (tuple, list)):
    return [str(index) for index in range(len(component))]

  elif inspect.isgenerator(component):
    # TODO: There are currently no commands available for generators.
    return []

  else:
    return [
        _FormatForCommand(member_name)
        for member_name, unused_member in _Members(component, verbose)
    ]


def _FormatForCommand(token):
  """Replaces underscores with hyphens, unless the token starts with a token.

  This is because we typically prefer hyphens to underscores at the command
  line, but we reserve hyphens at the start of a token for flags. This becomes
  relevant when --verbose is activated, so that things like __str__ don't get
  transformed into --str--, which would get confused for a flag.

  Args:
    token: The token to transform.
  Returns:
    The transformed token.
  """
  if not isinstance(token, six.string_types):
    token = str(token)

  if token.startswith('_'):
    return token
  else:
    return token.replace('_', '-')

M = {}

def _Seen(p):
  if p in M:
    return True
  M[p] = True

def _Commands(component, depth=3):
  """Yields tuples representing commands.

  To use the command from Python, insert '.' between each element of the tuple.
  To use the command from the command line, insert ' ' between each element of
  the tuple.

  Args:
    component: The component considered to be the root of the yielded commands.
    depth: The maximum depth with which to traverse the member DAG for commands.
  Yields:
    Tuples, each tuple representing one possible command for this CLI.
    Only traverses the member DAG up to a depth of depth.
  """

  if depth < 1:
    return

  for member_name, member in _Members(component):
    # Also skip components we've already seen.
    if _Seen(id(component)):
      continue

    member_name = _FormatForCommand(member_name)

    yield (member_name,)

    if inspect.isroutine(member) or inspect.isclass(member):
      for completion in Completions(member):
        yield (member_name, completion)
      continue  # Don't descend into routines.

    for command in _Commands(member, depth - 1):
      yield (member_name,) + command
