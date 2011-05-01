#!/usr/bin/python

import sys
import re
import wikidict

'''Converts Google Doc html into wikicode.'''

def getAttribute(tag):
  attr_regex = re.compile('</{0,1}([a-zA-Z0-9]*)[> ]')
  return attr_regex.match(tag).group(1)

# Uses two regex'es, can't find anything better for now
def getClass(tag):
  class_regex = re.compile('class="(.*)"')
  class_content = class_regex.search(tag).group(1)
  attr_regex = re.compile('[^ ]+')
  attr_match = attr_regex.findall(class_content)
  return attr_match

def tagType(tag):
  closing_tag = re.compile('^</')
  return 'opening' if (closing_tag.match(tag) is None) else 'closing'

def getFormat(attribute, wikidict, tag):
	format = ['', '']
	if attribute in wikidict:
		if 'noclass' in wikidict[attribute].keys():
			format = wikidict[attribute]['noclass']
		else:
			classes = getClass(tag)
			for class_name in classes:
				if class_name in wikidict[attribute].keys():
				 format = wikidict[attribute][class_name]
	return format

def wikicodify(input_filename, output_filename, wikidict):
	
	# Get Google Docs html
	input_file = open(input_filename, 'r')
	html = input_file.readline()
	input_file.close()
	
	# Open output filename for writing
	output = open(output_filename, 'w')
	
	# Define tags
	tagRegex = re.compile('<.*?>')
	iterator = tagRegex.finditer(html)
	attribute_stack = []
	format_stack = []
	
	content_start = 0
	for match in iterator:
		attribute = getAttribute(match.group())
		
		if(tagType(match.group()) == 'opening'):
			format = getFormat(attribute, wikidict, match.group())
			format_stack.append(format)
			output.write(format[0])
			content_start = match.end()
		else:
			content_end = match.start()
			# Print all the contents except the css
			if (attribute != 'style'):
				output.write(html[content_start:content_end])
			format = format_stack.pop()
			output.write(format[1])
			content_start = match.end()
	output.close()
	print 'Html to wikicode success!'

# File I/O
# input_file = raw_input('Enter .html file: ')
# output_file = raw_input('Enter output file: ')
# Get Google Docs css dictionary
wikidict_object = wikidict.Wikidict('SimpleDoc.html')
wikidict = wikidict_object.dict
wikicodify('SimpleDoc.html', 'test1.txt', wikidict)