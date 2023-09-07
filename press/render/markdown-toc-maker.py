#!/usr/bin/env python

import re
import sys

with open(sys.argv[1]) as fp:
	text = fp.read()

def reform(*,name,num=None):
	link = re.sub(r'[^\w\s]','',name)
	link = re.sub(r' ',r'-',link).lower()
	if num == None:
		return f'[{name:s}](#{link})'
	else:
		return f'{int(num):d}. [{name:s}](#{num}-{link})'

regex = r'^#+ (?P<num>\d+)\. (?P<name>.*?)$'
regex = r'^#+ (?P<name>.*?)$'

for item in re.finditer(regex,text,flags=re.M):
	s = reform(**item.groupdict())
	print(s)