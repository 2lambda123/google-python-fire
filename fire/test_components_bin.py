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

"""Python Fire test components Fire CLI.

This file is useful for replicating test results manually.
"""

import fire
from fire import test_components


def main():
  """Entry point for the program.

  This function uses the Fire library to automatically generate a command
  line interface for the test_components function.
  """

  fire.Fire(test_components)

if __name__ == '__main__':
  main()
