#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import os
import sys
import datetime as dt
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from vineland import Trestle, TrestleDocument, Dispatcher, TrestleObj
from openai import OpenAI

# yaml instance
yaml = YAML()
yaml.width = 80

# dev: hardcoded target file
spot = os.path.abspath(
	os.path.join(os.path.dirname(__file__),'..','data'))
if not os.path.isdir(spot):
	raise AssertionError(f'cannot find {spot}')

# hardcoded key ...!!!
if 0:
	default_name = 'llama3-8b-instruct-4bit'
	openai_key = "nope"
	base_url = "http://127.0.0.1:8080/v1"
else:
	default_name = '3p5turbo'
	with open(os.path.join(
		os.path.dirname(__file__),'..','.secret.openai.txt')) as fp:
		openai_key = fp.read().strip()
	base_url = None

### SETTINGS

def prepare_defaults(*,name):
	"""
	Organize sets of defaults.
	"""
	if name == '3p5turbo':
		settings = dict(
			answer=None,
			model='gpt-4-turbo', # 'gpt-4', # 'gpt-3.5-turbo',
			temperature=1.0,
			prompt=(
				'You are a helpful and honest assistant '
				'who values being precise and accurate.'),
			top_p=1.0,
			frequency_penalty=0,
			presence_penalty=0,
			max_tokens=2048,)
		return settings
	elif name == 'llama3-8b-instruct-4bit':
		settings = dict(
			answer=None,
			model=('/Users/ryanbradley/stage/local-llm/'
				'sandbox/model-llama3-8B--Instruct-4bit'),
			temperature=1.0,
			prompt=(
				'You are a helpful and honest assistant '
				'who values being precise and accurate.'),
			top_p=1.0,
			frequency_penalty=0,
			presence_penalty=0,
			max_tokens=2048,)
		return settings
	else:
		raise Exception(f'cannot find defaults named {name}')	

### INDEXERS

@Dispatcher
class ConversationIndexer:
	"""
	Transform root-level objects in the document via multiple dispatch by
	signature.
	"""
	def question_defaults_raw(self,*,q,
		temperature=None,model=None):
		settings = prepare_defaults(name=default_name)
		if temperature is not None:
			settings['temperature'] = temperature
		if model is not None:
			settings['model'] = model
		if isinstance(q,str):
			q = {'q':q}
		return QuestionAskOpenAI(
			question=Questioner(**q),
			**settings,)

@Dispatcher
class Questioner:
	"""
	Manage the question objects in the conversation
	"""
	def question_basic(self,*,q):
		return Question(question=q,refs=None)
	def question_basic_refs(self,*,q,refs):
		return Question(question=q,refs=refs)

### YAML OBJECTS

keys_globals = set(globals().keys())

class Conversation(TrestleDocument): 
	"""
	Supervise index file.
	"""
	yaml_tag = '!convo'
	trestle_dispatcher = ConversationIndexer

	def post(self):
		pass

class ScannerYAML(Trestle):
	"""Base class for round-trip YAML tagging and modification."""
	pass

class QuestionAskOpenAI(ScannerYAML):
	yaml_tag = '!question'
	# dev: the default name is redundant with ConversationIndexer
	requires_default = [
		'model','prompt','temperature','max_tokens',
		'top_p','frequency_penalty','presence_penalty',]

	def __init__(self,*,question,
		model=None,prompt=None,temperature=None,max_tokens=None,
		top_p=1.0,frequency_penalty=None,presence_penalty=None,
		usage=None,created=None,answer=None):
		self.question = question
		# required default values
		self.temperature = temperature
		self.model = model
		self.top_p = float(top_p)
		self.frequency_penalty = frequency_penalty
		self.presence_penalty = presence_penalty
		self.max_tokens = max_tokens
		self.prompt = prompt
		# make sure we complete the default values
		self.complete()
		# derived values
		self.usage = usage
		self.created = created
		self.answer = answer

	def complete(self):
		settings = prepare_defaults(name=default_name)
		for key in self.requires_default:
			if self.__dict__[key] is None:
				self.__dict__[key] = settings[key]

	def ask_chatgpt(self):
		"""
		Ask ChatGPT a question.
		"""
		global openai_key
		client = OpenAI(base_url=base_url,api_key=openai_key,)
		q_complete = self.question.get()
		print('status: asking …', end='\r')
		response_out = dict( 
			messages=[
				{"role": "system","content":self.prompt},
				{'role':'user','content':q_complete},],
			model=self.model,
			temperature=self.temperature,
			max_tokens=self.max_tokens,
			top_p=self.top_p,
			frequency_penalty=self.frequency_penalty,
			presence_penalty=self.presence_penalty,)
		if self.max_tokens == 'CUSTOM_NULL':
			response_out['max_tokens'] = None
		else:
			response_out['max_tokens'] = self.max_tokens
		response = client.chat.completions.create(**response_out)
		# trick to print done on the same line
		sys.stdout.flush()
		print('status: asking … done')
		# insist on a single answer
		x, = response.choices
		self.answer = x.message.content
		self.usage = response.usage.__dict__
		self.created = dt.datetime.fromtimestamp(
			response.created).strftime('%Y.%m.%d.%H%M.%S')

	@property
	def clean(self):
		out = dict(
			question=self.question)
		if self.answer is None:
			self.ask_chatgpt()
		out.update(
			top_p=self.top_p,
			frequency_penalty=self.frequency_penalty,
			presence_penalty=self.presence_penalty,
			max_tokens=self.max_tokens,
			prompt=LiteralScalarString(self.prompt),
			model=self.model,
			temperature=self.temperature)
		out['usage'] = self.usage
		out['created'] = self.created
		out['answer'] = self.answer
		return out

class Question(ScannerYAML):
	yaml_tag = '!question_posed'
	def __init__(self,*,question,refs=None):
		self.question = question
		self.refs = refs if refs else {}

	def get(self):
		refs_out = {}
		for key,val in self.refs.items():
			if isinstance(val,File):
				refs_out[key] = val.get()
			else:
				refs_out[key] = val
		return self.question.format(**refs_out)

	@property
	def clean(self):
		# via https://stackoverflow.com/a/57383273
		out = dict(question=LiteralScalarString(self.question))
		if self.refs:
			out['refs'] = self.refs
		return out

class File(ScannerYAML):
	yaml_tag = '!file'
	def __init__(self,*,path):
		self.path = path

	def get(self):
		with open(os.path.expanduser(self.path)) as fp:
			return fp.read()

	@property
	def clean(self):
		return dict(path=self.path)

class Refs(ScannerYAML):
	yaml_tag = '!refs'
	def __init__(self,*,path):
		self.path = path

	def get(self):
		with open(self.path) as fp:
			return fp.read()

	@property
	def clean(self):
		return dict(path=self.path)

### YAML INTERFACE

# automatically collect tags after defining yaml objects
tags_yaml_objects = [globals()[i] for i in globals().keys() - keys_globals]
		
### CLI FUNCTIONS

def talk():
	# build the trestle with the yaml tags
	fn = os.path.join(spot,'talker.yaml')
	trestle = TrestleObj(
		module=tags_yaml_objects,
		path=fn,)
	trestle.roundtrip()
