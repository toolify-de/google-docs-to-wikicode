import string
import re

class Wikidict:
  '''Constructs a wikicode dictionary from a Google Doc .html file 
     (Key, Value) pairs are in the form: (htmlElement, [leftWikicodetag, rightWikicodeTag])'''
  
  # Constructor
  def __init__(self, filename):
    self.filename = filename
    self.style = self.getStyle()  
    self.dict = self.getDict(self.getCSSDict())

  # Helper methods
  def getStyle(self):
    style_regex = re.compile('<style type="text/css">(.*)</style>')
    file_object = open(self.filename, "r")
    html = file_object.readline()
    file_object.close()
    return style_regex.search(html).group(1)
  
  def getCSSDict(self):
    '''Create a subdictionary of the form {classA:{attribute1:value1,attribute2:value2}, classB:...}''' 
    cssdict = {}
    class_regex = re.compile('\.(c\d*?)\{(.*?)\}')
    class_iterator = class_regex.finditer(self.style)
    for class_content in class_iterator:
       class_name = class_content.group(1)
       content = class_content.group(2)
       content_regex = re.compile('(.*?):([\d\w\.]*?);')
       cssdict[class_name] = {}
       content = content + ';' # hacky, don't judge me
       content_iterator = content_regex.finditer(content)
       for attr_val in content_iterator:
          attr = attr_val.group(1)
          val = attr_val.group(2)
          cssdict[class_name][attr] = val 
    return cssdict
  
  def getDict(self, cssdict):
    ''' Base dictionary of the form {element1:{class1:[format]}, element2:{class1:[format], class2:[format]}'''
    dict = { 'title':{'noclass':['=', '=\n']},
             'h1':{'noclass':['\n=','=\n']},
             'h2':{'noclass':['\n==', '==\n']},
             'h3':{'noclass':['\n===', '===\n']},
             'h4':{'noclass':['\n====', '====\n']},
             'h5':{'noclass':['\n=====', '=====\n']},
             'p': {'noclass':['\n','\n']},
             'b': {'noclass':["'''", "'''"]},
             'li': {}, 'span': {}, 'ol' : {}
            }
    dict = self.addLi(dict, cssdict)
    dict = self.addOther(dict, cssdict)
    return dict

  ## Element-specific helper functions ##

  # Sort classes according to 'margin-left' values and associate appropriate number of bullets (*)
  def addLi(self, dict, cssdict):	
    indents = []
    class_indent_map = {}
    for class_name in cssdict.keys():
      if 'margin-left' in cssdict[class_name]:
        indent = cssdict[class_name]['margin-left']
        if indent not in class_indent_map.keys():
			class_indent_map[indent] = [class_name]
			indents.append(indent)
        else:
			class_indent_map[indent].append(class_name)
    
    # Sort indents in increasing order
    maxlen = 0
    for indent in indents:
      if len(indent) > maxlen:
        maxlen = len(indent)
    for i in range(len(indents)):
      while len(indents[i]) < maxlen:
        indents[i] = '0' + indents[i] # basically pad with 0s so I can sort later
    indents.sort()
    for i in range(len(indents)):
      indents[i] = indents[i].lstrip('0')

	# Assign degree to li class
    degree = 1
    for indent in indents:
		degree = degree + 1
		classes = class_indent_map[indent]
		for class_name in classes:
			if class_name not in dict['li']:
				dict['li'][class_name] = [degree]
    return dict

  # Takes care of other elements: bold, italics, underlined text, type of lists (decimal or not)
  def addOther(self, dict, cssdict):
	for class_name in cssdict.keys():
		if ('font-weight' in cssdict[class_name]) and (cssdict[class_name]['font-weight'] == 'bold') and (class_name not in dict['span']):
			dict['span'][class_name] = ["'''", "'''"]
		if 'font-style' in cssdict[class_name] and cssdict[class_name]['font-style'] == 'italic' and class_name not in dict['span']:
			dict['span'][class_name] = ["''", "''"]
		if 'text-decoration' in cssdict[class_name] and cssdict[class_name]['text-decoration'] == 'underline' and class_name not in dict['span']:
			dict['span'][class_name] = ['<u>', '</u>']
		if 'list-style-type' in cssdict[class_name]:
			if cssdict[class_name]['list-style-type'] == 'decimal' and class_name not in dict['span']:
				dict['ol'][class_name] = '#'
			else:
				if class_name not in dict['span']:
					dict['ol'][class_name] = '*'					
	return dict
			

def debug():
   filename = raw_input('Enter filename: ')
   myDict = Wikidict(filename)
   print myDict.dict

if __name__ == '__main__':
   debug() 
