#!/usr/bin/python

import sys
import re
import wikidict

'''Converts Google Doc html into wikicode.'''

def get_element(tag):
  print tag
  return re.compile('</{0,1}([a-zA-Z0-9]*)[> ]').match(tag).group(1)

def get_class(tag):
  class_regex = re.compile('class="(.*?)"')
  if class_regex.search(tag) is None:
	return None
  class_content = class_regex.search(tag).group(1)
  return class_content.split()

# assumes opening tag
def get_attributes(tag):
	return re.compile('(\w*)="([^"]*)"').findall(tag)

def get_tag_type(tag):
  closing_tag = re.compile('^</')
  return 'opening' if (closing_tag.match(tag) is None) else 'closing'

def get_format(element, wikidict, tag):
	formats = []
	if element not in wikidict.keys():
		return [ '', '']
	else:
		element_classes = wikidict[element].keys()
		if 'noclass' in element_classes:
			formats.append(wikidict[element]['noclass'])
		elif 'default' in element_classes or 'append' in element_classes:
			classes = get_class(tag)
			if 'append' in element_classes:
				formats.append(wikidict[element]['append'])
			if 'default' in element_classes and classes is None:
				formats.append(wikidict[element]['default'])
			if classes is not None:
				for class_name in get_class(tag):
					if class_name in element_classes:
						formats.append(wikidict[element][class_name])
		else:
			tag_classes = get_class(tag)
			for class_name in tag_classes:
				if class_name in element_classes:
					formats.append(wikidict[element][class_name])
		if element == 'table':
			for attribute in get_attributes(tag):
				if attribute[0] == 'class':
					1 #formats.append(wikidict[element][class_name])
				else:
					formats.append([' ' + attribute[0] + '="' + attribute[1] + '"', ''])
			1 # TODO: take into account table attributes (cellpadding, cellspacing, border etc.)
	format_before = ''
	format_after = ''
	for format_list in formats:
			if len(format_list) == 2:
				format_before += format_list[0]
				format_after = format_list[1] + format_after
			else:
				return format_list[0]
	return [format_before, format_after]

def update_elements_stack(elements_stack):
	new_degree = elements_stack['formats'][-1]
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
		if element == 'p':
			print elements_stack['elements']
		if element == 'table':
			elements_stack['table']['insert_break'] = False
		if element == 'li':
			elements_stack = update_elements_stack(elements_stack)
			bullet_type = elements_stack['li']['bullet_type']
			bullet_nb = elements_stack['li']['limap'][elements_stack['formats'][-1]]
			output.write('\n' + bullet_type * bullet_nb)
			print '\n', bullet_type * bullet_nb
		elif element == 'ol':
			elements_stack['li']['bullet_type'] = elements_stack['formats'][-1]
		elif element == 'p'and elements_stack['elements'][-2] == 'td':
				if elements_stack['table']['insert_break'] == False:
					elements_stack['table']['insert_break'] = True
				else:
					output.write('<br/>') # write nothing (p defaults to a return carriage and we don't want that)
		else:
			format = elements_stack['formats'][-1][0]
			if len(format) > 0:
				output.write(format)
				print 'A: >', format
	# if the tag is a closing tag
	if tag_type == 'closing':
		last_element_format = elements_stack['formats'].pop()
		# print 'popped closing element', element, 'with format', format, 'from the above format_stack'
		if (element == 'p'and elements_stack['elements'][-1] == 'td') or (element == 'li') or (element == 'ol'):
			1 # write nothing (p defaults to a return carriage and we don't want that)
		else:
			format = last_element_format[1]
			if len(format) > 0:
				output.write(last_element_format[1])
				print elements_stack['elements']
				print 'B: >', last_element_format[1]		
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
	elements_stack = {'li': {'li_bullet_type' : '*','limap' :{}, 'liref' : liref }, 
					  'table': {'insert_break': False},
					  'formats': [], 
					  'elements' : [] }
	
	content_start = 0
	ignore_br_at = 0
	for match in iterator:
		element = get_element(match.group())
		if(get_tag_type(match.group()) == 'opening'):
			if(element != 'br'): # Tu m'as donne du fil a retordre toi
				elements_stack['elements'].append(element)
				format = get_format(element, wikidict, match.group())
				elements_stack['formats'].append(format)
				elements_stack = print_format('opening', element, elements_stack, output)
				content_start = match.end()
			else:
				ignore_br_at = match.start()
		else:
			content_end = match.start()
			elements_stack['elements'].pop()
			# Print all the contents except the css
			if (element != 'style'):
					if ignore_br_at > 0:
						output.write(html[content_start:ignore_br_at]+ '\n' + html[ignore_br_at + 4 :content_end])
						ignore_br_at = 0
					else:
						if content_start != content_end:
							output.write(html[content_start:content_end])
							print '-->', html[content_start:content_end]	
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