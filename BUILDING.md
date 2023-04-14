Notes for developers
====================

Making a poetry environment on Windows
--------------------------------------
Use the following to obtain a poetry-managed environment for a specific python
version on Windows

poetry env use (py -3.7 -c "import sys; print(sys.executable)")

This repo has the poetry_py_version script to do this.
