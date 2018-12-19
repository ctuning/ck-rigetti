# CK repository for Rigetti's pyQuil API

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](http://cTuning.org/ae)
[![workflow](https://github.com/ctuning/ck-guide-images/blob/master/ck-workflow.svg)](http://cKnowledge.org)

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Travis Build Status](https://travis-ci.org/ctuning/ck-rigetti.svg?branch=master)](https://travis-ci.org/ctuning/ck-rigetti)

* [pyQuil's code](https://github.com/rigetti/pyquil) on gitHub.
* [pyQuil's official documentation](https://pyquil.readthedocs.io/en/stable/) on ReadTheDocs.

## List of dependencies:
- *Python 3.6+* ([required by pyQuil](https://pyquil.readthedocs.io/en/stable/start.html); [CK supports 2.7 and 3.3+](https://github.com/ctuning/ck#minimal-installation)).
- *git* (required by CK, is usually installed on modern Operating Systems)
- [Collective Knowledge](http://cknowledge.org).


## Installation (on Ubuntu)

### Install Python 3 and its pip:

```
$ sudo apt-get install python3 python3-pip
```

### Install Collective Knowledge:

```
$ sudo python3 -m pip install ck
```


## Installation (on MacOSX)

### Install Python 3.6 and its pip:
```
$ brew update
$ brew unlink python
$ brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/f2a764ef944b1080be64bd88dca9a1d80130c558/Formula/python.rb
$ export PATH=/usr/local/opt/python/bin:$PATH   # better to put this into your .bashrc config file to avoid repeating in every terminal window
```

### Install Collective Knowledge:

```
$ python3 -m pip install ck
```


## Common part of the installation

### Download the pre-compiled Quantum Compiler and Simulator:

Visit [Rigetti Forest SDK download page](https://www.rigetti.com/forest)
and follow their instructions to obtain two pre-compiled binaries
for your operating system: *qvm* (the local Simulator) and *quilc* (the local Quil compiler).

Then let CK know where it was installed:
```
$ ck detect soft:local.forest
```


### Detect a Python 3 interpreter (interactively choose one if there are several options)
```
$ ck detect soft:compiler.python --default_selection="3."
```

### Install this CK repository with all its dependencies (other CK repos to reuse artifacts)
```
$ ck pull repo:ck-rigetti
```

### Install a specific version of pyQuil API package:

```
$ ck install package:lib-pyquil-multiversion --force_version=2.1.0
```

### Run your local QVM (the Simulator) in server mode (leave this terminal window open and switch to another one):

```
$ ck run program:qvm-server
```


## Run some simple tests to see that your setup is working:

#### Run a demo program (select interactively from a menu)

```
$ ck run program:pyquil-demo
```

#### Run the hello-world demo (a Python runner + default hello_world.quil file)

```
$ ck run program:pyquil-demo --cmd_key=from-quil-file
```

#### Run a given .quil file (path relative to tmp directory or absolute)

```
$ ck run program:pyquil-demo --cmd_key=from-quil-file --env.QUIL_FILE=../teleport.quil
```

#### Run the dedicated teleportation demo in Python

```
$ ck run program:pyquil-demo --cmd_key=teleportation
```

#### Run a given pyQuil example (path relative to pyQuil example directory in CK-TOOLS)
```
$ ck run program:pyquil-demo --cmd_key=from-pyquil-examples --env.PYQUIL_EXAMPLE=pointer.py
```


## Run an interactive python session with access to CK-installed pyQuil

#### shell-bound IPython session:
```
$ ck virtual env --tags=lib,pyquil --shell_cmd=ipython

In [1]: import pyquil

In [2]: ...
```

#### Jupyter Notebook session in your browser:
```
$ ck virtual env --tags=lib,pyquil --shell_cmd='jupyter notebook'

In [1]: import pyquil

In [2]: ...
```
