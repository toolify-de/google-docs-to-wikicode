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
  class_regex = re.compile('class="(.*?)"')
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
			print 'format returned for attribute', attribute, 'and classes', classes, 'is', format
	return format

def printFormat(tagType, attribute, format_stack, special_stack, output):
	# if the tag is an opening tag
	if tagType == 'opening':
		start_format = format_stack[-1][0] # i.e. last start_format	
		if attribute == 'li':
			# special_stack['li'] is a list of tuples ('degree', 'format')
			bullet = special_stack['listatus']['bullet']
			if len(special_stack['li']) == 0:
				bullets = '\n' + bullet
			else:
				lastli = special_stack['li'][-1]
				degree = lastli[0]
				bullets = lastli[1]
				if special_stack['listatus']['new'] == True: 
					bullets = '\n' + bullet
					special_stack['listatus']['new'] = False
				elif start_format > degree:
					bullets = bullets + bullet
				elif start_format < degree:
					bullets = bullets[0:-1]
				else:
					bullets = bullets
					# It means start_format == bullets, in other words, don't change the list level.
			special_stack['li'].append((start_format, bullets))
			output.write(bullets)
		elif attribute == 'ol':
			print 'attribute is ol, specialstack[-1] ==', format_stack[-1]
			special_stack['listatus']['bullet'] = format_stack[-1]
		else:
			output.write(start_format)
		if attribute[0] == 'h':
			special_stack['listatus']['new'] = True
	# if the tag is a closing tag
	if tagType == 'closing':
		print 'format_stack', format_stack
		format = format_stack.pop()
		print 'popped closing attribute', attribute, 'with format', format, 'from the above format_stack'
 		if attribute != 'li' and attribute != 'ol':
			end_format = format[1]
			output.write(end_format)
				
	return {'format_stack': format_stack, 'special_stack': special_stack}
	
def wikicodify(input_filename, output_filename, wikidict):
	print wikidict
	
	# Get Google Docs html
	input_file = open(input_filename, 'r')
	html = input_file.readline()
	input_file.close()
	
	# Open output filename for writing
	output = open(output_filename, 'w')
	
	# Define tags
	tagRegex = re.compile('<.*?>')
	iterator = tagRegex.finditer(html)
	format_stack = []
	
	# Special elements
	special_stack = {'li': [], 'listatus': {'bullet': '*', 'new': True }}
	
	content_start = 0
	ignore_next_element = False
	for match in iterator:
		attribute = getAttribute(match.group())
		
		if(tagType(match.group()) == 'opening'):
			if(attribute != 'br'): # Tu m'as donne du fil a retordre toi
				format = getFormat(attribute, wikidict, match.group())
				format_stack.append(format)
				stacks = printFormat('opening', attribute, format_stack, special_stack, output)
				format_stack = stacks['format_stack']
				special_stack = stacks['special_stack']
			content_start = match.end()
		else:
			content_end = match.start()
			# Print all the contents except the css
			if (attribute != 'style'):
					output.write(html[content_start:content_end])
					print '--->', html[content_start:content_end]
			stacks = printFormat('closing', attribute, format_stack, special_stack, output)
			format_stack = stacks['format_stack']
			special_stack = stacks['special_stack']			
			content_start = match.end()
			
	output.close()
	print 'Html to wikicode success!'

# File I/O
input_file = raw_input('Enter .html file: ')
output_file = raw_input('Enter output file: ')
# Get Google Docs css dictionary
wikidict_object = wikidict.Wikidict(input_file)
wikidict = wikidict_object.dict
wikicodify(input_file, output_file, wikidict)