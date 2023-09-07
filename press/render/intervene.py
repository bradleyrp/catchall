#!/usr/bin/env python

import sys
import re

regex_comment_blank = r'^[\t\s]*-- .*?$',''
regex_comment_highlight = r'^[\t\s]*--! (.*?)\n',r'<br><mark>\1</mark><br>'

text_out = sys.stdin.read()
for target,rep in [
	regex_comment_blank,
	regex_comment_highlight,
	]:
	text_out = re.sub(target,rep,text_out,flags=re.M)
print(text_out)
