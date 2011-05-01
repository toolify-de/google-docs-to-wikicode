#!/usr/bin/python

import sys
import string
import re
import wikidict

def getAttribute(parent_match):
  tag = parent_match.group()
  attr_regex = re.compile('</{0,1}([a-zA-Z0-9]*)[> ]')
  return attr_regex.match(tag).group(1)

def getClass(line, match_object):
  fulltag = line[match_object.start():match_object.end()]
  class_regex = re.compile('class="(.*)"')
  class_content = class_regex.search(fulltag).group(1)
  attr_regex = re.compile('[^ ]+')
  attr_match = attr_regex.findall(class_content)
  return attr_match # Uses two regex'es, can't find anything better for now

def wikicode(line, wikidict, stack, start, end):
  parent_match = stack[-1] # currently the last opening tag
  parent = getAttribute(parent_match)
  wikiline = ''  
  i = -1;

  while parent not in wikidict.keys():
    i = i - 1;
    if -i >= len(stack):
      return ""
    parent_match = stack[i]
    parent = getAttribute(parent_match)
  
  format = ['', '']
  if parent in wikidict:
    if 'noclass' in wikidict[parent].keys():
      format = wikidict[parent]['noclass']
    else:
      classes = getClass(line, parent_match)
      for class_name in classes: # Lol now the serious business would be combining a list with bold text, ouch (still not implemented)
       if class_name in wikidict[parent].keys():
          format = wikidict[parent][class_name]
    return (format[0] + line[start:end] + format[1])
  return line[start:end]

def isClosingTag(tag):
  ct = re.compile('^</')
  if ct.match(tag) is None:
    return False
  else:
    return True

def getOutput(line, wikidict):
  # Define tags
  tagRegex = re.compile('<.*?>') # ('<[a-zA-Z"=/ ]*>')
  iterator = tagRegex.finditer(line)
  stack = [] # stack of match objects
  output = [] # list of wikicode lines

  prev = "" # Keeps track of the previous tag
  for match in iterator:
     cur = getAttribute(match)
 
     if isClosingTag(match.group()) == False:
       stack.append(match)
       start = match.end()  # The start of the content is the end of the opening tag
       prev = getAttribute(match)
     else:
       end = match.start()  #The end of the content is the beginning of the closing tag 
       if prev == cur:
         output.append(wikicode(line, wikidict, stack, start, end))
       stack.pop() # this could be useful for debugging later
  return output

# File I/O
html = raw_input('Enter .html file: ')
txt = raw_input('Enter output file: ')
wikidict_object = wikidict.Wikidict(html)
wikidict = wikidict_object.dict
input_file = open(html, 'r')
line = input_file.readline() # LOL Google Docs output html as a single line
input_file.close()
output = getOutput(line, wikidict) 

output_file = open(txt, 'w')
output_file.write('\n'.join(output))
output_file.write('\n')
output_file.close()
