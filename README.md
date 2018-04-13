# ck-rigetti


* [pyQuil's code](https://github.com/rigetticomputing/pyquil) on gitHub.
* [pyQuil's official documentation](http://pyquil.readthedocs.io/en/latest/) on ReadTheDocs.

## Obtaining your Forest API key and user_id

Visit [Rigetti Forest sign-up page](https://www.rigetti.com/index.php/forest)
and follow their instructions to obtain two strings: api_key and user_id .
Make a note of them, they will be needed at a later step.


## Installation (on Ubuntu)

### Install global prerequisites, Python and its pip (Python2 is also supported)

```
$ sudo apt-get install python3 python3-pip
```

### Install Collective Knowledge

```
$ sudo pip3 install ck
```


## Installation (on MacOSX)

### Install Python3 and its Pip3 (Python2 is also supported)

```
$ brew update
$ brew reinstall python
```

### Install Collective Knowledge

```
$ pip install ck
```


## Common part of the installation

### Detect a Python interpreter (interactively choose one if there are several options)
```
$ ck detect soft:compiler.python
```

### Install this CK repository with all its dependencies (other CK repos to reuse artifacts)
```
$ ck pull repo:ck-rigetti
```

### List all the packages available 

```
$ ck list ck-rigetti:package:*
```

### Install CK package for pyQuil (insert your api_key and user_id that you obtained by registering - see above)

```
$ ck install package:lib-pyquil \
        --env.PYQUIL_FOREST_API_KEY=xnmRPAVunQl19TtQz9eMd11iiIsArtUDTaEnsSV6uy \
        --env.PYQUIL_USER_ID=015a1263b-d7f2-426d-b2f5-2fe2e9727d1d0
```


## Run a simple test
```
$ echo $HOME/CK/ck-rigetti/t/ck_pyquil_test.sh $HOME/CK/ck-rigetti/t/pyquil_test.py | ck virtual env --tags=pyquil
```

