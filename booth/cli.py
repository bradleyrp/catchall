#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import click
from vineland import debugger_click

# import calculation functions
from .booth import talk

def cli_hook():
	"""Expose the CLI to __main__ and/or console_scripts."""
	cli_parent(obj={})

@click.group('booth')
@click.help_option('-h','--help')
@click.option('--debug',is_flag=True,default=False)
@click.pass_context
def cli_parent(ctx,debug):
	"""
	Router for the `catchall.sci` code. Sends commands to subcommands.
	"""
	# via https://click.palletsprojects.com/en/8.0.x/commands/
	# ensure that ctx.obj exists and is a dict in case `cli` is called elsewhere
	ctx.ensure_object(dict)
	ctx.obj['DEBUG'] = debug

@cli_parent.command('talk')
@click.help_option('-h','--help')
@click.pass_context
@debugger_click
def talk_cli(): 
	"""Perform an example calculation."""
	return talk()