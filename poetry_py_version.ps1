# Make a poetry python environment on Windows using a specific version of
# python, discovered using the 'py' command
# Python version is accepted as a command-line argument

# poetry run <command> will run <command> in the environment
# poetry shell makes a new shell in the specified environment

# This script is ineffective if the config setting 
virtualenvs.in-project = null and .venv exists or
virtualenvs.in-project = true (in which case .venv is always used)

param ($py_version = $(throw "Python version parameter is required."))

poetry env use (py -$py_version -c 'import sys; print(sys.executable)')

