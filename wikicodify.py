#!/usr/bin/python

import sys
import re
import wikidict

'''Converts Google Doc html into wikicode.'''

def get_element(tag):
  element_regex = re.compile('</{0,1}([a-zA-Z0-9]*)[> ]')
  return element_regex.match(tag).group(1)

def get_class(tag):
  class_regex = re.compile('class="(.*?)"')
  class_content = class_regex.search(tag).group(1)
  return class_content.split()

def get_tag_type(tag):
  closing_tag = re.compile('^</')
  return 'opening' if (closing_tag.match(tag) is None) else 'closing'

def get_format(element, wikidict, tag):
	format = ['', '']
	if element in wikidict:
		if 'noclass' in wikidict[element].keys():
			format = wikidict[element]['noclass']
		else:
			classes = get_class(tag)
			for class_name in classes:
				if class_name in wikidict[element].keys():
					format = wikidict[element][class_name]
	return format

def update_elements_stack(elements_stack):
	new_degree = elements_stack['formats'][-1][0]
	# If special_stacl['limap'] is empty, build it with the default values
	if len(elements_stack['li']['limap']) == 0:
		i = 1
		for ith_degree in elements_stack['li']['liref']:
			if ith_degree not in elements_stack['li']['limap']:
				elements_stack['li']['limap'][ith_degree] = i
				i = i + 1
	else: 
		# The original map definition should work for most cases, exceptions should be handled here
		1
		# TODO: 
		# if there is a switch from numbered bullets to unnumbered bullets (problem occurs in BIOL201LN21.html)
		# 
		
	return elements_stack

def print_format(tag_type, element, elements_stack, output):
	# if the tag is an opening tag
	if tag_type == 'opening':
		start_format = elements_stack['formats'][-1][0] # i.e. last start_format	
		# print 'start_format', start_format
		if element == 'li':
			elements_stack = update_elements_stack(elements_stack)
			bullet_type = elements_stack['li']['bullet_type']
			bullet_nb = elements_stack['li']['limap'][elements_stack['formats'][-1][0]]
			output.write('\n' + bullet_type * bullet_nb)
		elif element == 'ol':
			elements_stack['li']['bullet_type'] = elements_stack['formats'][-1]
		else:
			output.write(start_format)
	# if the tag is a closing tag
	if tag_type == 'closing':
		last_element_format = elements_stack['formats'].pop()
		# print 'popped closing element', element, 'with format', format, 'from the above format_stack'
 		if element != 'li' and element != 'ol':
			output.write(last_element_format[1])		
	return elements_stack
	
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
	
	# Stacks
	format_stack = []
	liref = []
	for i in wikidict['li'].values():
		for j in i:
			liref.append(j)
	liref.sort()
	elements_stack = {'li': {'li_bullet_type' : '*','limap' :{}, 'liref' : liref }, 'formats': [], }
	
	content_start = 0
	ignore_br_at = 0
	for match in iterator:
		element = get_element(match.group())
		if(get_tag_type(match.group()) == 'opening'):
			if(element != 'br'): # Tu m'as donne du fil a retordre toi
				format = get_format(element, wikidict, match.group())
				elements_stack['formats'].append(format)
				elements_stack = print_format('opening', element, elements_stack, output)
				content_start = match.end()
			else:
				ignore_br_at = match.start()
		else:
			content_end = match.start()
			# Print all the contents except the css
			if (element != 'style'):
					if ignore_br_at > 0:
						output.write(html[content_start:ignore_br_at]+ '\n' + html[ignore_br_at + 4 :content_end])
						ignore_br_at = 0
					else:
						output.write(html[content_start:content_end])
						# print '-->', html[content_start:content_end]	
			elements_stack = print_format('closing', element, elements_stack, output)		
			content_start = match.end()
	output.close()
	print 'Html to wikicode success!'

# File I/O
# input_file = raw_input('Enter .html file: ')
# output_file = raw_input('Enter output file: ')
# Get Google Docs css dictionary
input_file = 'BIOL201LN21.html'
output_file = 'test.txt'
wikidict_object = wikidict.Wikidict(input_file)
wikidict = wikidict_object.dict
wikicodify(input_file, output_file, wikidict)