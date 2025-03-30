#!/usr/bin/env python
from .cli import cli_hook
# hook the CLI to runpy for this package
if __name__ == '__main__':
	cli_hook()