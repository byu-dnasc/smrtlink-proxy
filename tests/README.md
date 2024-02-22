# Using pytest

To run the tests, install `pytest`. Also, you can run pytest in the vscode debug menu 
using the debugger launch configuration `.vscode/launch.json`.

## Launch configuration

In addition to allowing you to run the Python Debugger from vscode's debug menu, the launch
configuration file (`.vscode/launch.json`) specifies two helpful options:
- Only tests found under `tests` will be run
- `pytest` will halt upon a failure (remove `-x` option to revert)