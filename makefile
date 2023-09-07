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
.PHONY: install installall clean test notebook press
all:
	@echo "usage: \"make install\" creates a virtual environment"
	@echo "usage: \"source ./go.sh\" sources the environment from anywhere"

# install a local venv
venv:
	python3 -m venv venv

# make sure we track with git
.git:
	git init

# install the standard package
install: venv .git
	venv/bin/pip install -U -e .

# install the science package
HAS_MPICC := $(shell command -v mpicc 2> /dev/null)
allinstall: venv .git
ifndef DOT
	$(error "mpicc is not available")
endif
	venv/bin/pip install -U -e .[all]

# uninstall
clean:
	rm -rf build catchall.egg-info venv

# perform unit tests
test:
	venv/bin/python -m unittest 

# fire up a jupyter notebook
notebook:
	echo "warning: use Firefox on MacOS due to weird blank page issue"
	python -m notebook --no-browser

# render documentation
press:
	@bash -c "eval \"$$(luarocks path --bin)\" && make -s -C press"