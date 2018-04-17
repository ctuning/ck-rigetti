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


## Run some simple tests

#### Run a demo program (select interactively from a menu)

```
$ ck run program:pyquil-demo
```

#### Run the hello-world demo (a Python runner + a .quil file)

```
$ ck run program:pyquil-demo --cmd_key=hello-world
```

#### Run the teleportation demo (a Python script)

```
$ ck run program:pyquil-demo --cmd_key=teleportation
```

