#!/usr/bin/env python

import os.path

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# note that if you modify scope you have to remove token.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive']

# settings
kind_mime = dict(
	docx=('application/vnd.openxmlformats-'
		'officedocument.wordprocessingml.document'))

def get_service():
	"""
	Shows basic usage of the Drive v3 API.
	Prints the names and ids of the first 10 files the user has access to.
	"""
	global service
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())
	try:
		service = build('drive', 'v3', credentials=creds)
	except HttpError as error:
		# TODO(developer) - Handle errors from drive API.
		print(f'An error occurred: {error}')
	return service

def search_file(q):
	global service
	try:
		files = []
		page_token = None
		while True:
			response = service.files().list(
				q=q,
				spaces='drive',
				fields=
					'nextPageToken, '
				  	'files(id, name)',
				pageToken=page_token).execute()
			for file in response.get('files', []):
				# Process change
				print(F'Found file: {file.get("name")}, {file.get("id")}')
			files.extend(response.get('files', []))
			page_token = response.get('nextPageToken', None)
			if page_token is None:
				break
	except HttpError as error:
		print(F'An error occurred: {error}')
		files = None
	return files

def create_folder(*,name,parent_id=None):
	file_metadata = {
		'name': name,
		'mimeType': 'application/vnd.google-apps.folder'}
	if parent_id:
		file_metadata['parents'] = [parent_id]
	file = service.files().create(
		body=file_metadata,
		fields='id,name,kind').execute()
	return file

def get_or_create_top_folder(*,dn,root_abs_dn='root'):
	# get the root
	root = service.files().list(
		q=f"'{root_abs_dn}' in parents and trashed = false"
		).execute()
	# get the root directory for our documentation
	base = [i for i in root['files'] if i['name']==dn]
	if len(base) > 1:
		raise Exception(f'redundant "{dn}" in root')
	elif len(base) == 0:
		base = create_folder(name=dn)
	else:
		base = base[0]
	return base

def create_or_update_file(*,name,source,parent_id,mimetype):
	# see if the file exists
	found = search_file(
		q=f'"{parent_id}" in parents and name="{name}" and trashed=false')
	file_metadata = {'name': name}
	media = MediaFileUpload(source,mimetype=mimetype)
	if len(found) > 1:
		raise Exception('found duplicate files named "{name}"')
	elif len(found) == 0:
		file_metadata['parents'] = [parent_id]
		file = service.files().create(
			body=file_metadata, 
			media_body=media,
			fields='id').execute()
	else:
		file_update_id = found[0]['id']
		file = service.files().update(
			fileId=file_update_id,
			body=file_metadata, 
			media_body=media,
			fields='id').execute()
	return file

def update_permissions(*,file_id,
	users_readers=None,domains_readers=None,users_writers=None):
	if not users_readers:
		users_readers = []
	if not users_writers:
		users_writers = []
	if not domains_readers:
		domains_readers = []
	ids = []
	def callback(request_id, response, exception):
		if exception:
			print(exception)
		else:
			print(f'Request_Id: {request_id}')
			print(F'Permission Id: {response.get("id")}')
			ids.append(response.get('id'))
	batch = service.new_batch_http_request(callback=callback)
	for email in users_readers:
		user_permission = {
			'type':'user',
			'role':'reader',
			'emailAddress':email,}
		batch.add(service.permissions().create(fileId=file_id,
			body=user_permission,
			sendNotificationEmail=False,
			fields='id',))
	for email in users_writers:
		user_permission = {
			'type':'user',
			'role':'writer',
			'emailAddress':email,}
		batch.add(service.permissions().create(fileId=file_id,
			body=user_permission,
			sendNotificationEmail=False,
			fields='id',))
	for domain in domains_readers:
		domain_permission = {
			'type':'domain',
			'role':'reader',
			'domain':domain, }
		batch.add(service.permissions().create(
			fileId=file_id,
			body=domain_permission,
			sendNotificationEmail=False,
			fields='id',))
	batch.execute()

def push_gdoc_basic(*,name,base_dn,source,
	users_readers=None,users_writers=None,domains_readers=None,kind=None):
	"""Intermediary to push files to google drive."""
	global service
	get_service()
	# get base directory
	base = get_or_create_top_folder(dn=base_dn)
	if kind == None:
		if name.endswith('.docx'):
			kind = 'docx'
		else:
			raise Exception(f'cannot infer kind for: kind={kind}, name={name}, '
				f'base_dn={base_dn}, source={source}')
	# update file
	try:
		kwargs = dict(
			parent_id=base['id'],
			name=name,
			mimetype=kind_mime[kind],
			source=source)
		file = create_or_update_file(**kwargs)
	except:
		raise Exception(f'failed to update (consider printing to pub?): "{kwargs}"')
	# attach permissions
	update_permissions(
		file_id=file['id'],
		users_readers=users_readers,
		users_writers=users_writers,
		domains_readers=domains_readers)

if __name__ == '__main__':

	# settings
	base_dn = 'lurcdocs'

	# get service
	get_service()

	# example code
	if 0:
		push_gdoc_basic(
			base_dn=base_dn,
			name='test.docx',
			kind='docx',
			source='/Users/ryanbradley/stage/test.docx',
			users_readers=['bradleyrp@gmail.com'])
