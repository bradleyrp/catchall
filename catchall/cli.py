#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import click
import time

# import calculation functions
from catchall.work import compute_worker
from catchall.work import read_output

@click.group('catchall')
@click.help_option('-h','--help')
@click.option('--debug',is_flag=True,default=False)
@click.pass_context
def cli_parent(ctx,debug):
	"""
	Router for the `catchall` code. Sends commands to subcommands.
	"""
	# via https://click.palletsprojects.com/en/8.0.x/commands/
	# ensure that ctx.obj exists and is a dict in case `cli` is called elsewhere
	ctx.ensure_object(dict)
	ctx.obj['DEBUG'] = debug

@cli_parent.command('calc')
@click.help_option('-h','--help')
@click.option('-n','--num',help='Number of iterations',default=10)
def worker_example_cli(*,num): 
	"""Perform an example calculation."""
	return compute_worker(num=num)

@cli_parent.command('read')
@click.help_option('-h','--help')
def read_example_cli(): 
	"""Summarize the data we already collected."""
	return read_output()

@cli_parent.command('parallel')
@click.help_option('-h','--help')
@click.option('-n','--num',help='Number of iterations',default=10)
def worker_example_parallel_cli(*,num): 
	"""Perform an example of parallel writes."""
	# importing here in case mpi4py is not available
	# dev: make this a separate extras requirement in setup
	from .parallel import compute_worker_parallel
	return compute_worker_parallel(num=num)

### CLI

def cli_hook():
	"""Expose the CLI to __main__ and/or console_scripts."""
	cli_parent(obj={})

if __name__ == '__main__':
	cli_hook()
