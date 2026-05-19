# ReHeat

A Python-based decision support tool for evaluating and optimizing hybrid industrial process heat systems.

## Install 

Make sure you have a working version of Python, the code was developed using Python 3.12.0.  
There are multiple ways to do this: you can install the python version [directly](https://www.python.org/downloads/), use a Python version manager like [pyenv](https://github.com/pyenv/pyenv) (extra steps for [Windows](https://github.com/pyenv-win/pyenv-win)) or a Python package and version manager like [anaconda](https://www.anaconda.com/download). 

For example, using pyenv you can install Python 3.12.0:

        pyenv install 3.12.0

Activate it for the current session:

        pyenv local 3.12.0

Next, create a virtual environment and activate it:
        
        python -m venv env
        source env/bin/activate (Windows: source env/Scripts/activate)

Install the required packages (from pyproject.toml):

        pip install -e .

The Linear Programming model requires a solver to be installed. Examples include CBC, XPRESS, Gurobi, CPLEX.
Instructions to use the open-source solver CBC can be found [here](https://github.com/coin-or/Cbc) (different steps for Windows and Unix).

## Usage

A minimal example of how to use the package:

        python examples/run_reheat.py

A more detailed example on how to use the package and functions is provided in the jupyter notebook `examples/analysis.ipynb`.
