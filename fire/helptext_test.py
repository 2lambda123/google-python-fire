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

"""Tests for the helptext module."""

import os
import sys
import textwrap

from fire import formatting
from fire import helptext
from fire import test_components as tc
from fire import testutils
from fire import trace
import six


class HelpTest(testutils.BaseTestCase):

  def setUp(self):
    """Set up the test environment for HelpTest.

    This method sets up the test environment by disabling ANSI colors before
    running the test cases.
    """

    super(HelpTest, self).setUp()
    os.environ['ANSI_COLORS_DISABLED'] = '1'

  def testHelpTextNoDefaults(self):
    """Test the help text for a component with no defaults.

    This function initializes a component with no defaults and generates
    help text for it. It then checks if the help text contains specific
    sections and excludes others.

    Args:
        self: The test case instance.
    """

    component = tc.NoDefaults
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='NoDefaults'))
    self.assertIn('NAME\n    NoDefaults', help_screen)
    self.assertIn('SYNOPSIS\n    NoDefaults', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextNoDefaultsObject(self):
    """Test the help text for NoDefaults object.

    This function creates a NoDefaults object and generates help text for
    it. It then checks for the presence of specific information in the help
    text.

    Args:
        self: The test case object.
    """

    component = tc.NoDefaults()
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='NoDefaults'))
    self.assertIn('NAME\n    NoDefaults', help_screen)
    self.assertIn('SYNOPSIS\n    NoDefaults COMMAND', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('COMMANDS\n    COMMAND is one of the following:',
                  help_screen)
    self.assertIn('double', help_screen)
    self.assertIn('triple', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunction(self):
    """Test the HelpText function by checking the generated help text content.

    This function creates a HelpText object with a specified component and
    trace, then checks if certain strings are present or absent in the
    generated help text.

    Args:
        self: The test case object.
    """

    component = tc.NoDefaults().double
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double COUNT', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('POSITIONAL ARGUMENTS\n    COUNT', help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  def testHelpTextFunctionWithDefaults(self):
    """Test the HelpText function with default values.

    This function tests the HelpText function by creating a HelpText object
    with default values and checking the presence of specific strings in the
    help screen.
    """

    component = tc.WithDefaults().triple
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='triple'))
    self.assertIn('NAME\n    triple', help_screen)
    self.assertIn('SYNOPSIS\n    triple <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    -c, --count=COUNT\n        Default: 0',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunctionWithLongDefaults(self):
    """Test the HelpText function with long default values.

    This function initializes a component with default values and creates a
    HelpText object using the component and a FireTrace object. It then
    performs various assertions on the generated help screen.

    Args:
        self: The test case object.
    """

    component = tc.WithDefaults().text
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='text'))
    self.assertIn('NAME\n    text', help_screen)
    self.assertIn('SYNOPSIS\n    text <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    -s, --string=STRING\n'
        '        Default: \'0001020304050607080910'
        '1112131415161718192021222324252627282...',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunctionWithKwargs(self):
    """Test the HelpText function with keyword arguments.

    This function sets up a HelpText object with a specified component and
    trace for testing purposes. It then checks if certain expected strings
    are present in the generated help screen.

    Args:
        self: The test case object.
    """

    component = tc.fn_with_kwarg
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='text'))
    self.assertIn('NAME\n    text', help_screen)
    self.assertIn('SYNOPSIS\n    text ARG1 ARG2 <flags>', help_screen)
    self.assertIn('DESCRIPTION\n    Function with kwarg', help_screen)
    self.assertIn(
        'FLAGS\n    --arg3\n        Description of arg3.\n    '
        'Additional undocumented flags may also be accepted.',
        help_screen)

  def testHelpTextFunctionWithKwargsAndDefaults(self):
    """Test the HelpText function with keyword arguments and defaults.

    This function sets up a HelpText object with a specified component and
    trace for testing purposes. It then checks if specific strings are
    present in the generated help screen.

    Args:
        self: The test class instance.
    """

    component = tc.fn_with_kwarg_and_defaults
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='text'))
    self.assertIn('NAME\n    text', help_screen)
    self.assertIn('SYNOPSIS\n    text ARG1 ARG2 <flags>', help_screen)
    self.assertIn('DESCRIPTION\n    Function with kwarg', help_screen)
    self.assertIn(
        'FLAGS\n    -o, --opt=OPT\n        Default: True\n'
        '    The following flags are also accepted.'
        '\n    --arg3\n        Description of arg3.\n    '
        'Additional undocumented flags may also be accepted.',
        help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithDefaultsAndTypes(self):
    """Test the HelpText function with defaults and types.

    This function creates a HelpText object with a specified component and
    trace. It then checks for the presence of certain strings in the help
    screen output.

    Args:
        self: The test class instance.
    """

    component = (
        tc.py3.WithDefaultsAndTypes().double)  # pytype: disable=module-attr
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double <flags>', help_screen)
    self.assertIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    -c, --count=COUNT\n        Type: float\n        Default: 0',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithTypesAndDefaultNone(self):
    """Test the help text function with types and default value of None.

    This function initializes a component with defaults and types, then
    creates a help text object using the component and a FireTrace object.
    It performs assertions to check the content of the help text.

    Args:
        self: The test case instance.
    """

    component = (
        tc.py3.WithDefaultsAndTypes().get_int)  # pytype: disable=module-attr
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='get_int'))
    self.assertIn('NAME\n    get_int', help_screen)
    self.assertIn('SYNOPSIS\n    get_int <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    -v, --value=VALUE\n'
        '        Type: Optional[int]\n        Default: None',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithTypes(self):
    """Test the help text function with types.

    This function creates a help text screen for a component with types. It
    checks if the generated help text contains specific information such as
    component name, synopsis, description, positional arguments, and notes.
    """

    component = tc.py3.WithTypes().double  # pytype: disable=module-attr
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double COUNT', help_screen)
    self.assertIn('DESCRIPTION', help_screen)
    self.assertIn(
        'POSITIONAL ARGUMENTS\n    COUNT\n        Type: float',
        help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithLongTypes(self):
    """Test the help text function with long types.

    This function tests the help text generation for a component with long
    types. It creates a HelpText object for the specified component and
    trace, and then checks for the presence of certain strings in the help
    text.

    Args:
        self: The test class instance.
    """

    component = tc.py3.WithTypes().long_type  # pytype: disable=module-attr
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='long_type'))
    self.assertIn('NAME\n    long_type', help_screen)
    self.assertIn('SYNOPSIS\n    long_type LONG_OBJ', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    # TODO(dbieber): Assert type is displayed correctly. Type displayed
    # differently in Travis vs in Google.
    # self.assertIn(
    #     'POSITIONAL ARGUMENTS\n    LONG_OBJ\n'
    #     '        Type: typing.Tuple[typing.Tuple['
    #     'typing.Tuple[typing.Tuple[typing.Tupl...',
    #     help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  def testHelpTextFunctionWithBuiltin(self):
    """Test the HelpText function with a built-in component.

    This function creates a HelpText object for a specified component and
    trace. It then checks if certain strings are present in the generated
    help screen.

    Args:
        self: The test class instance.
    """

    component = 'test'.upper
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'upper'))
    self.assertIn('NAME\n    upper', help_screen)
    self.assertIn('SYNOPSIS\n    upper', help_screen)
    # We don't check description content here since the content is python
    # version dependent.
    self.assertIn('DESCRIPTION\n', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunctionIntType(self):
    """Test the HelpText function for the int type component.

    This function initializes a HelpText object for the 'int' component and
    checks for specific content in the help screen.

    Args:
        self: The test case object.
    """

    component = int
    help_screen = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'int'))
    self.assertIn('NAME\n    int', help_screen)
    self.assertIn('SYNOPSIS\n    int', help_screen)
    # We don't check description content here since the content is python
    # version dependent.
    self.assertIn('DESCRIPTION\n', help_screen)

  def testHelpTextEmptyList(self):
    """Test the HelpText class when the component list is empty.

    This function creates a HelpText object with an empty component list and
    a FireTrace object. It then asserts the presence of certain strings in
    the help_screen output.

    Args:
        self: The test case object.
    """

    component = []
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'list'))
    self.assertIn('NAME\n    list', help_screen)
    self.assertIn('SYNOPSIS\n    list COMMAND', help_screen)
    # TODO(zuhaochen): Change assertion after custom description is
    # implemented for list type.
    self.assertNotIn('DESCRIPTION', help_screen)
    # We don't check the listed commands either since the list API could
    # potentially change between Python versions.
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)

  def testHelpTextShortList(self):
    """Test the HelpText class for a short list component.

    This function initializes a HelpText object with a short list component
    and a FireTrace object. It then checks for specific strings in the help
    screen output.

    Args:
        self: The test case object.
    """

    component = [10]
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'list'))
    self.assertIn('NAME\n    list', help_screen)
    self.assertIn('SYNOPSIS\n    list COMMAND', help_screen)
    # TODO(zuhaochen): Change assertion after custom description is
    # implemented for list type.
    self.assertNotIn('DESCRIPTION', help_screen)

    # We don't check the listed commands comprehensively since the list API
    # could potentially change between Python versions. Check a few
    # functions(command) that we're confident likely remain available.
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)
    self.assertIn('     append\n', help_screen)

  def testHelpTextInt(self):
    """Test the HelpText class for integer component.

    It initializes a HelpText object for a specific integer component and
    checks for the presence of certain strings in the help screen.

    Args:
        self: The test case object.
    """

    component = 7
    help_screen = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, '7'))
    self.assertIn('NAME\n    7', help_screen)
    self.assertIn('SYNOPSIS\n    7 COMMAND | VALUE', help_screen)
    # TODO(zuhaochen): Change assertion after implementing custom
    # description for int.
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)
    self.assertIn('VALUES\n    VALUE is one of the following:\n', help_screen)

  def testHelpTextNoInit(self):
    """Test the generation of help text when no initialization is provided.

    This function creates an instance of HelpText class with a component and
    trace. It then checks if the generated help text contains specific
    strings.

    Args:
        self: The test case instance.
    """

    component = tc.OldStyleEmpty
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'OldStyleEmpty'))
    self.assertIn('NAME\n    OldStyleEmpty', help_screen)
    self.assertIn('SYNOPSIS\n    OldStyleEmpty', help_screen)

  @testutils.skipIf(
      six.PY2, 'Python 2 does not support keyword-only arguments.')
  def testHelpTextKeywordOnlyArgumentsWithDefault(self):
    """Test the help text generation for a component with keyword-only
    arguments and defaults.

    This function tests the generation of help text for a component with
    keyword-only arguments and defaults.

    Args:
        self: The test case instance.
    """

    component = tc.py3.KeywordOnly.with_default  # pytype: disable=module-attr
    output = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'with_default'))
    self.assertIn('NAME\n    with_default', output)
    self.assertIn('FLAGS\n    -x, --x=X', output)

  @testutils.skipIf(
      six.PY2, 'Python 2 does not support keyword-only arguments.')
  def testHelpTextKeywordOnlyArgumentsWithoutDefault(self):
    """Test the generation of help text for a component with keyword-only
    arguments without default values.

    This function creates a HelpText object for a specified component with a
    FireTrace object and checks if certain strings are present in the
    output.

    Args:
        self: The test case object.
    """

    component = tc.py3.KeywordOnly.double  # pytype: disable=module-attr
    output = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'double'))
    self.assertIn('NAME\n    double', output)
    self.assertIn('FLAGS\n    -c, --count=COUNT (required)', output)

  @testutils.skipIf(
      six.PY2,
      'Python 2 does not support required name-only arguments.')
  def testHelpTextFunctionMixedDefaults(self):
    """Test the HelpTextComponent with a function having mixed default
    arguments.

    This function creates a HelpTextComponent object and checks if the
    expected output contains specific strings.
    """

    component = tc.py3.HelpTextComponent().identity
    t = trace.FireTrace(component, name='FunctionMixedDefaults')
    output = helptext.HelpText(component, trace=t)
    self.assertIn('NAME\n    FunctionMixedDefaults', output)
    self.assertIn('FunctionMixedDefaults <flags>', output)
    self.assertIn('--alpha=ALPHA (required)', output)
    self.assertIn('--beta=BETA\n        Default: \'0\'', output)

  @testutils.skipIf(
      six.PY2,
      'Python 2 does not support required name-only arguments.')
  def testHelpTextFunctionMixedDefaults(self):
    """Test the HelpTextComponent with a function containing mixed default
    arguments.

    It creates a HelpTextComponent instance and a FireTrace instance with
    the given component name. Then it generates help text for the component
    and checks for specific strings in the output.

    Args:
        self: The test case instance.
    """

    component = tc.py3.HelpTextComponent().identity
    t = trace.FireTrace(component, name='FunctionMixedDefaults')
    output = helptext.HelpText(component, trace=t)
    self.assertIn('NAME\n    FunctionMixedDefaults', output)
    self.assertIn('FunctionMixedDefaults <flags>', output)
    self.assertIn('--alpha=ALPHA (required)', output)
    self.assertIn('--beta=BETA\n        Default: \'0\'', output)

  def testHelpScreen(self):
    """Test the help screen output for a specific component.

    This function creates an instance of ClassWithDocstring, initializes a
    FireTrace object, and then generates the help text using HelpText. It
    compares the generated help text with the expected output.
    """

    component = tc.ClassWithDocstring()
    t = trace.FireTrace(component, name='ClassWithDocstring')
    help_output = helptext.HelpText(component, t)
    expected_output = """
NAME
    ClassWithDocstring - Test class for testing help text output.

SYNOPSIS
    ClassWithDocstring COMMAND | VALUE

DESCRIPTION
    This is some detail description of this test class.

COMMANDS
    COMMAND is one of the following:

     print_msg
       Prints a message.

VALUES
    VALUE is one of the following:

     message
       The default message to print."""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpScreenForFunctionDocstringWithLineBreak(self):
    """Test the help screen for a function docstring with line breaks.

    This function tests the help screen output for a function docstring with
    line breaks. It compares the expected output with the actual help output
    after formatting.
    """

    component = tc.ClassWithMultilineDocstring.example_generator
    t = trace.FireTrace(component, name='example_generator')
    help_output = helptext.HelpText(component, t)
    expected_output = """
    NAME
        example_generator - Generators have a ``Yields`` section instead of a ``Returns`` section.

    SYNOPSIS
        example_generator N

    DESCRIPTION
        Generators have a ``Yields`` section instead of a ``Returns`` section.

    POSITIONAL ARGUMENTS
        N
            The upper limit of the range to generate, from 0 to `n` - 1.

    NOTES
        You can also use flags syntax for POSITIONAL ARGUMENTS"""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpScreenForFunctionFunctionWithDefaultArgs(self):
    """Test the help screen for the function with default arguments.

    It creates a component with default arguments, generates a FireTrace
    object, and then compares the help text output with the expected output.
    """

    component = tc.WithDefaults().double
    t = trace.FireTrace(component, name='double')
    help_output = helptext.HelpText(component, t)
    expected_output = """
    NAME
        double - Returns the input multiplied by 2.

    SYNOPSIS
        double <flags>

    DESCRIPTION
        Returns the input multiplied by 2.

    FLAGS
        -c, --count=COUNT
            Default: 0
            Input number that you want to double."""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpTextUnderlineFlag(self):
    """Test the generation of help text with underline formatting flag.

    This function creates a help text for a given component with underline
    formatting flag. It checks if the generated help text contains specific
    formatting elements.

    Args:
        self: The test case instance.
    """

    component = tc.WithDefaults().triple
    t = trace.FireTrace(component, name='triple')
    help_screen = helptext.HelpText(component, t)
    self.assertIn(formatting.Bold('NAME') + '\n    triple', help_screen)
    self.assertIn(
        formatting.Bold('SYNOPSIS') + '\n    triple <flags>',
        help_screen)
    self.assertIn(
        formatting.Bold('FLAGS') + '\n    -c, --' +
        formatting.Underline('count'),
        help_screen)

  def testHelpTextBoldCommandName(self):
    """Test the formatting of help text for a command name in bold.

    This function initializes a ClassWithDocstring object, creates a
    FireTrace object, and generates a HelpText object to display the help
    text for the command name in bold.

    Args:
        self: The test case object.
    """

    component = tc.ClassWithDocstring()
    t = trace.FireTrace(component, name='ClassWithDocstring')
    help_screen = helptext.HelpText(component, t)
    self.assertIn(
        formatting.Bold('NAME') + '\n    ClassWithDocstring', help_screen)
    self.assertIn(formatting.Bold('COMMANDS') + '\n', help_screen)
    self.assertIn(
        formatting.BoldUnderline('COMMAND') + ' is one of the following:\n',
        help_screen)
    self.assertIn(formatting.Bold('print_msg') + '\n', help_screen)

  def testHelpTextObjectWithGroupAndValues(self):
    """Test the help text object with group and values.

    This function creates a TypedProperties object and a FireTrace object.
    It then creates a HelpText object with the given component, trace, and
    verbose parameters. The function prints the help screen and asserts that
    certain strings are present in the help screen.
    """

    component = tc.TypedProperties()
    t = trace.FireTrace(component, name='TypedProperties')
    help_screen = helptext.HelpText(
        component=component, trace=t, verbose=True)
    print(help_screen)
    self.assertIn('GROUPS', help_screen)
    self.assertIn('GROUP is one of the following:', help_screen)
    self.assertIn(
        'charlie\n       Class with functions that have default arguments.',
        help_screen)
    self.assertIn('VALUES', help_screen)
    self.assertIn('VALUE is one of the following:', help_screen)
    self.assertIn('alpha', help_screen)

  def testHelpTextNameSectionCommandWithSeparator(self):
    """Test the generation of help text with a specified separator for a
    command section name.

    This function creates a FireTrace object with a specified component and
    name, and separator. It then adds a separator to the trace object and
    generates help text using the component, trace, and verbose flag. The
    function asserts that the generated help text contains the specified
    separator and does not contain duplicate separators.

    Args:
        self: The test case instance.
    """

    component = 9
    t = trace.FireTrace(component, name='int', separator='-')
    t.AddSeparator()
    help_screen = helptext.HelpText(component=component, trace=t, verbose=False)
    self.assertIn('int -', help_screen)
    self.assertNotIn('int - -', help_screen)

  def testHelpTextNameSectionCommandWithSeparatorVerbose(self):
    """Test the generation of help text with name, section, command, separator,
    and verbose mode.

    It creates a test instance of a component with default values, sets up a
    FireTrace object with specific parameters, adds a separator, and
    generates help text. Then, it checks if certain strings are present in
    the help text.
    """

    component = tc.WithDefaults().double
    t = trace.FireTrace(component, name='double', separator='-')
    t.AddSeparator()
    help_screen = helptext.HelpText(component=component, trace=t, verbose=True)
    self.assertIn('double -', help_screen)
    self.assertIn('double - -', help_screen)

  def testHelpTextMultipleKeywoardArgumentsWithShortArgs(self):
    """Test the help text generation for a function with multiple keyword
    arguments and short arguments.

    It creates a test instance of a component with multiple default values,
    sets up a FireTrace object, and generates a HelpText object to capture
    the help screen output. The function then asserts the presence of
    specific text elements within the help screen output.

    Args:
        self: The test case instance.
    """

    component = tc.fn_with_multiple_defaults
    t = trace.FireTrace(component, name='shortargs')
    help_screen = helptext.HelpText(component, t)
    self.assertIn(formatting.Bold('NAME') + '\n    shortargs', help_screen)
    self.assertIn(
        formatting.Bold('SYNOPSIS') + '\n    shortargs <flags>',
        help_screen)
    self.assertIn(
        formatting.Bold('FLAGS') + '\n    -f, --first',
        help_screen)
    self.assertIn('\n    --last', help_screen)
    self.assertIn('\n    --late', help_screen)



class UsageTest(testutils.BaseTestCase):

  def testUsageOutput(self):
    """Test the usage output for a component.

    This function creates a component with no defaults, creates a FireTrace
    object, and generates the usage text for the component. It then compares
    the generated output with the expected output.
    """

    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: NoDefaults <command>
      available commands:    double | triple

    For detailed information on this command, run:
      NoDefaults --help"""

    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputVerbose(self):
    """Test the verbose usage output for the NoDefaults command.

    This function creates an instance of NoDefaults component and a
    FireTrace object with the component. It then generates the usage text
    for the component with verbose information.

    Returns:
        str: The verbose usage output for the NoDefaults command.
    """

    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: NoDefaults <command>
      available commands:    double | triple

    For detailed information on this command, run:
      NoDefaults --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputMethod(self):
    """Test the UsageOutputMethod function.

    This function tests the UsageOutputMethod by creating a component with
    no defaults, creating a FireTrace object, adding accessed properties to
    the trace, and generating usage text using helptext. It then compares
    the generated output with the expected output.

    Args:
        self: The test case object.
    """

    component = tc.NoDefaults().double
    t = trace.FireTrace(component, name='NoDefaults')
    t.AddAccessedProperty(component, 'double', ['double'], None, None)
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: NoDefaults double COUNT

    For detailed information on this command, run:
      NoDefaults double --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithHelp(self):
    """Test the usage output for the function_with_help command.

    This function sets up the necessary components to test the usage output
    for the function_with_help command. It creates a FireTrace object and a
    UsageText object to capture the usage output and compare it with the
    expected output.

    Args:
        self: The test case object.
    """

    component = tc.function_with_help
    t = trace.FireTrace(component, name='function_with_help')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: function_with_help <flags>
      optional flags:        --help

    For detailed information on this command, run:
      function_with_help -- --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithDocstring(self):
    """Test the usage output function with docstring.

    This function sets up a test for the usage output of the
    multiplier_with_docstring component. It creates a FireTrace object and a
    UsageText object to check the expected output against the actual output.

    Args:
        self: The test case object.
    """

    component = tc.multiplier_with_docstring
    t = trace.FireTrace(component, name='multiplier_with_docstring')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: multiplier_with_docstring NUM <flags>
      optional flags:        --rate

    For detailed information on this command, run:
      multiplier_with_docstring --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  @testutils.skipIf(
      six.PY2,
      'Python 2 does not support required name-only arguments.')
  def testUsageOutputFunctionMixedDefaults(self):
    """Test the usage output for a function with mixed defaults.

    This function creates a help text component and a fire trace for a
    function with mixed defaults. It then generates the usage text for the
    component with the given trace and verbosity settings. Finally, it
    compares the expected output with the generated usage output.
    """

    component = tc.py3.HelpTextComponent().identity
    t = trace.FireTrace(component, name='FunctionMixedDefaults')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: FunctionMixedDefaults <flags>
      optional flags:        --beta
      required flags:        --alpha

    For detailed information on this command, run:
      FunctionMixedDefaults --help"""
    expected_output = textwrap.dedent(expected_output).lstrip('\n')
    self.assertEqual(expected_output, usage_output)

  def testUsageOutputCallable(self):
    """Test the usage output for a CallableWithKeywordArgument component.

    This function creates a CallableWithKeywordArgument component and a
    FireTrace object with specified arguments. It then generates the usage
    text for the component and compares it with the expected output.

    Args:
        self: The test case object.
    """

    # This is both a group and a command.
    component = tc.CallableWithKeywordArgument()
    t = trace.FireTrace(component, name='CallableWithKeywordArgument',
                        separator='@')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: CallableWithKeywordArgument <command> | <flags>
      available commands:    print_msg
      flags are accepted

    For detailed information on this command, run:
      CallableWithKeywordArgument -- --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputConstructorWithParameter(self):
    """Test the UsageOutput constructor with parameters.

    This function creates an instance of InstanceVars and FireTrace classes,
    then generates a UsageText object. It compares the generated output with
    the expected output after dedenting and stripping leading newline
    characters.

    Args:
        self: The test case object.
    """

    component = tc.InstanceVars
    t = trace.FireTrace(component, name='InstanceVars')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: InstanceVars --arg1=ARG1 --arg2=ARG2

    For detailed information on this command, run:
      InstanceVars --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputConstructorWithParameterVerbose(self):
    """Test the UsageOutput constructor with the parameter 'verbose'.

    This function creates an instance of InstanceVars, initializes a
    FireTrace object, and then creates a UsageText object with verbose set
    to True. It compares the expected output with the generated usage
    output.
    """

    component = tc.InstanceVars
    t = trace.FireTrace(component, name='InstanceVars')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: InstanceVars <command> | --arg1=ARG1 --arg2=ARG2
      available commands:    run

    For detailed information on this command, run:
      InstanceVars --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputEmptyDict(self):
    """Test the usage output for an empty dictionary.

    This function creates an empty dictionary and then generates the usage
    text for it using the helptext module.

    Args:
        self: The test case instance.
    """

    component = {}
    t = trace.FireTrace(component, name='EmptyDict')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: EmptyDict

    For detailed information on this command, run:
      EmptyDict --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputNone(self):
    """Test the usage output when component is None.

    This function creates a FireTrace object with a component as None and
    generates usage text. It then compares the generated output with the
    expected output.

    Returns:
        str: The usage output text.
    """

    component = None
    t = trace.FireTrace(component, name='None')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: None

    For detailed information on this command, run:
      None --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testInitRequiresFlagSyntaxSubclassNamedTuple(self):
    """Test the initialization of a subclass named tuple with required flag
    syntax.

    This function creates an instance of SubPoint subclass and initializes
    it with required flag syntax. It then generates the usage text for the
    component and checks if the expected output is present.

    Args:
        self: The test case instance.
    """

    component = tc.SubPoint
    t = trace.FireTrace(component, name='SubPoint')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = 'Usage: SubPoint --x=X --y=Y'
    self.assertIn(expected_output, usage_output)

if __name__ == '__main__':
  testutils.main()
