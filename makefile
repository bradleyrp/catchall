### SHORTCUTS via MAKEFILE

# via: https://stackoverflow.com/a/66310588
PYTHON=$(shell command -v python3)
ifeq (, $(PYTHON))
    $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif
PYTHON_VERSION_MIN=3.8
PYTHON_VERSION_CUR=$(shell $(PYTHON) -c 'import sys; print("%d.%d"% sys.version_info[0:2])')
PYTHON_VERSION_OK=$(shell $(PYTHON) -c 'import sys; cur_ver = sys.version_info[0:2]; min_ver = tuple(map(int, "$(PYTHON_VERSION_MIN)".split("."))); print(int(cur_ver >= min_ver))')
ifeq ($(PYTHON_VERSION_OK), 0)
    $(error "Need python version >= $(PYTHON_VERSION_MIN). Current version is $(PYTHON_VERSION_CUR)")
endif

# shortcut list
.PHONY: install clean test
all:

# install a local venv
venv:
	python3 -m venv venv

# make sure we track with git
.git:
	git init

# install this package
install: venv .git
	venv/bin/pip install -U -e .

# uninstall
clean:
	rm -rf build catchall.egg-info venv

# perform unit tests
test:
	venv/bin/python -m unittest 
