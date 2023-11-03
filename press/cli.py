#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import click
import time
import os

# dev: the cursesmenu package cannot exit and write to stdout which is too bad
#   because we found great utility from using ortho.textviewer in books scan
from simple_term_menu import TerminalMenu

from .render.gpress import push_gdoc_basic

# settings
raw_press_path = ('press/raw',)
raw_press_pub_path = ('press/pub',)
router_fn = 'router.yaml'

# build the trestle with the yaml tags
from ortho import Trestle, TrestleDocument, Dispatcher, build_trestle
from ortho import yaml_str
from ruamel.yaml import YAML,yaml_object
yaml = YAML(typ='rt')
yaml.width = 80

# save the global keys before defining objects with yaml_tag
keys_globals = set(globals().keys())

@Dispatcher
class GDriveIndexBuilder:
	def kind_gdoc(self,shortname,source,target,kind,spot=None):
		return GDoc(
			shortname=shortname,source=source,
			target=target,kind=kind,spot=spot)
	def kind_gdrive(self,spot=None):
		return GDrive(spot=spot)

class GDriveIndex(TrestleDocument): 
	"""
	Supervise index file.
	"""
	yaml_tag = '!gdrive_index'
	trestle_dispatcher = GDriveIndexBuilder
	def post(self):
		shortnames = []
		# collect defaults
		gdrive_found = [i for i in self.data if i.yaml_tag == GDrive.yaml_tag]
		if len(gdrive_found) > 2:
			raise Exception(f'redundant "{GDrive.yaml_tag}" items')
		# apply defaults downward to GDoc objects
		if len(gdrive_found) == 1:
			gdrive = gdrive_found[0]
			for item in self.data:
				if item.yaml_tag == GDoc.yaml_tag:
					if item.spot == None:
						item.spot_out = gdrive.spot
					if item.shortname in shortnames:
						raise Exception(
							f'shortname collision: {item.shortname}')
					if item.domain and gdrive.domain:
						item.domain_out = gdrive.domain
					shortnames.append(item.shortname)

class GDoc(Trestle):
	yaml_tag = '!gdoc'
	def __init__(self,*,source,target,shortname,kind=None,spot=None,
		writers=None,readers=None,domain=False):
		self.spot = spot
		if spot:
			self.spot_out = spot
		self.target = target
		self.shortname = shortname
		self.kind = kind
		self.writers = writers
		self.readers = readers
		self.domain = domain
		self.domain_out = None
		# the domain can be a boolean or a target otherwise we inherit from a
		#   single GDrive object that sets the defaults
		if self.domain and not isinstance(self.domain,bool):
			self.domain_out = domain
		# dev: hardcoded path relative to makefile entrypoint
		self.source = source
		source_abs = os.path.join(os.getcwd(),*raw_press_pub_path,source)
		if os.path.isfile(source_abs):
			self.source_abs = source_abs
		else:
			source_abs = os.path.join(*raw_press_pub_path,source)
			if os.path.isfile(source_abs):
				self.source_abs = source_abs
			else:
				raise Exception(f'cannot find "{source}" or "{source_abs}"')
	def push(self):
		print(
			f'status: {yaml_str(yaml=yaml,obj=dict(push=self.__dict__))}')
		if self.domain and not self.domain_out:
			raise Exception('failed to get a domain') 
		if not isinstance(self.domain_out,list):
			self.domain_out = [self.domain_out]
		push_gdoc_basic(
			name=self.target,
			base_dn=self.spot_out,
			source=self.source_abs,
			kind=self.kind,
			users_readers=self.readers,
			users_writers=self.writers,
			domains_readers=self.domain_out)
	@property
	def clean(self):
		out = {}
		if self.spot:
			out['spot'] = self.spot
		out.update(
			shortname=self.shortname,
			source=self.source,
			target=self.target)
		if self.writers:
			out['writers'] = self.writers
		if self.readers:
			out['readers'] = self.readers
		if self.domain:
			out['domain'] = self.domain
		return out

class GDrive(Trestle):
	yaml_tag = '!gdrive'
	def __init__(self,*,spot=None,domain=None):
		self.spot = spot
		# promote the domain to a list of readers
		self.domain = [domain]
	@property
	def clean(self):
		out = {}
		if self.spot:
			out['spot'] = self.spot
		if self.domain:
			# allow only one domain for now
			if len(self.domain) > 1:
				raise AssertionError
			out['domain'] = self.domain[0]
		return out

# automatically collect tags after defining yaml objects
tags_yaml_objects = [i for i in globals().keys() - keys_globals]
tags_yaml_objects = [globals()[tag] for tag in globals().keys() - keys_globals 
	if hasattr(globals().get(tag,None),'yaml_tag')]

def get_router():
	"""Collect a gdrive router."""
	# dev: path relative to makefile entrypoint
	router_fn_abs = os.path.join(*raw_press_path,router_fn)
	if not os.path.isfile(router_fn_abs):
		raise Exception(f'cannot find {router_fn_abs}')

	trestle,trestle_text = build_trestle(
		tags=tags_yaml_objects,
		yaml=yaml,get_text_completer=True)
	# nb postprocessing happens automatically
	doc = trestle(router_fn_abs)
	return doc

def gpress_menu():
	"""
	Create a curses menu to publish gdocs to Google Drive
	"""
	doc = get_router()
	options = [item.shortname for item in doc.data if
		item.yaml_tag == GDoc.yaml_tag] + ['quit']
	terminal_menu = TerminalMenu(options)
	result = terminal_menu.show()
	router = dict([(i,j) for i,j in enumerate(options)])
	if router[result] == 'quit':
		return
	found = [i for i in doc.data 
		if i.yaml_tag == GDoc.yaml_tag and 
		i.shortname == router[result]]
	if len(found) == 0:
		raise Exception(f'cannot find "{shortname}"')
	elif len(found) > 1:
		raise Exception(f'collision on "{shortname}"')
	found = found[0]
	kwargs = dict(
		base_dn=found.spot_out,
		name=found.target,
		source=found.source_abs,
		users_readers=found.readers,
		users_writers=found.writers,
		domains_readers=found.domain_out)
	print(f'status: push: {kwargs}')
	push_gdoc_basic(**kwargs)

@click.group('gpress')
@click.help_option('-h','--help')
@click.option('--debug',is_flag=True,default=False)
@click.pass_context
def cli_parent(ctx,debug):
	"""
	Router for the `gpress` code. Sends commands to subcommands.
	"""
	# via https://click.palletsprojects.com/en/8.0.x/commands/
	# ensure that ctx.obj exists and is a dict in case `cli` is called elsewhere
	ctx.ensure_object(dict)
	ctx.obj['DEBUG'] = debug

@cli_parent.command('doc')
@click.help_option('-h','--help')
@click.argument('target')
def gpress_pub_cli(*,target): 
	"""Publish a gdoc to Google Drive."""
	router = get_router()
	found = []
	for item in router.data:
		if item.yaml_tag == GDoc.yaml_tag:
			if item.shortname == target:
				found.append(item)
	if not found:
		raise Exception(f'cannot find "{target}"')
	elif len(found) > 2:
		raise Exception(f'redundant matches for "{target}"')
	else:
		found[0].push()

@cli_parent.command('menu')
@click.help_option('-h','--help')
def worker_example_cli(): 
	"""Use the gpress menu to publish documents."""
	gpress_menu()

### CLI

def cli_hook():
	"""Expose the CLI to __main__ and/or console_scripts."""
	cli_parent(obj={})
