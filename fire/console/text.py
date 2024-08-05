# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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
"""Semantic text objects that are used for styled outputting."""

import enum


class TextAttributes(object):
  """Attributes to use to style text with."""

  def __init__(self, format_str=None, color=None, attrs=None):
    """Defines a set of attributes for a piece of text.

    Args:
      format_str: (str), string that will be used to format the text
        with. For example '[{}]', to enclose text in brackets.
      color: (Colors), the color the text should be formatted with.
      attrs: (Attrs), the attributes to apply to text.
    """
    self._format_str = format_str
    self._color = color
    self._attrs = attrs or []

  @property
  def format_str(self):
    """Return the format string used for formatting.

    Returns:
        str: The format string used for formatting.
    """

    return self._format_str

  @property
  def color(self):
    """Return the color of the object.

    Returns:
        str: The color of the object.
    """

    return self._color

  @property
  def attrs(self):
    """Return the attributes of the object.

    This function returns the attributes of the object.

    Returns:
        dict: A dictionary containing the attributes of the object.
    """

    return self._attrs


class TypedText(object):
  """Text with a semantic type that will be used for styling."""

  def __init__(self, texts, text_type=None):
    """String of text and a corresponding type to use to style that text.

    Args:
     texts: (list[str]), list of strs or TypedText objects
       that should be styled using text_type.
     text_type: (TextTypes), the semantic type of the text that
       will be used to style text.
    """
    self.texts = texts
    self.text_type = text_type

  def __len__(self):
    """Calculate the total length of all texts in the instance.

    This method iterates through all texts in the instance and calculates
    the total length by summing the length of each text.

    Returns:
        int: The total length of all texts combined.
    """

    length = 0
    for text in self.texts:
      length += len(text)
    return length

  def __add__(self, other):
    """Add two TypedText objects together.

    Combines the current TypedText object with another TypedText object by
    creating a new TypedText object containing the texts from both objects.

    Args:
        self (TypedText): The first TypedText object.
        other (TypedText): The second TypedText object to be added.

    Returns:
        TypedText: A new TypedText object containing the texts from both input objects.
    """

    texts = [self, other]
    return TypedText(texts)

  def __radd__(self, other):
    """Return a new TypedText object by concatenating the current TypedText
    object with another object in reverse order.

    Args:
        self (TypedText): The current TypedText object.
        other (object): The object to be concatenated with the current TypedText object.

    Returns:
        TypedText: A new TypedText object created by concatenating the current TypedText
            object with the other object in reverse order.
    """

    texts = [other, self]
    return TypedText(texts)


class _TextTypes(enum.Enum):
  """Text types base class that defines base functionality."""

  def __call__(self, *args):
    """    Returns a TypedText object using this style.

    This function takes variable arguments and returns a TypedText object
    with the provided arguments and the current style.

    Args:
        *args: Variable number of arguments.

    Returns:
        TypedText: An object of TypedText class.
    """
    return TypedText(list(args), self)


# TODO: Add more types.
class TextTypes(_TextTypes):
  """Defines text types that can be used for styling text."""
  RESOURCE_NAME = 1
  URL = 2
  USER_INPUT = 3
  COMMAND = 4
  INFO = 5
  URI = 6
  OUTPUT = 7
  PT_SUCCESS = 8
  PT_FAILURE = 9

