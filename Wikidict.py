import string
import re

class Wikidict:
  '''constructs a dictionary from a Google Doc .html file - it will probably be extended to other formats'''
  
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
    class_regex = re.compile('(\.c\d*?)\{(.*?)\}')
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
    dict = { 'title':{'noclass':['=', '=']},
             'h4':{'noclass':['====', '====']},
             'h3':{'noclass':['===', '===']},
             'h2':{'noclass':['==', '==']},
             'h1':{'noclass':['=','=']},
             'p': {'noclass':['','']},
             'a': {'noclass':['','']},
             'b': { 'noclass':["'''", "'''"] },
             'li': {}
            }

    # li degrees ugh.. Sort classes according to 'margin-left' values and associate appropriate *
    indents = []
    class_indent_map = {}
    for class_name in cssdict.keys():
      if 'margin-left' in cssdict[class_name]:
        indent = cssdict[class_name]['margin-left']
        class_indent_map[indent] = class_name
        indents.append(indent)
    
    # What I'm about to do is super hacky, forgive me
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
    
    for i in range(len(indents)):
      class_name = class_indent_map[indents[i]]
      if class_name not in dict['li']:
         degree = '*' * (i + 1) # i.e. the first element at index 0 has 1 bullet
         dict['li'][class_name] = [degree, '']
    return dict

def debug():
   filename = raw_input('Enter filename: ')
   myDict = Wikidict(filename)
   print myDict.dict

if __name__ == '__main__':
   debug() 
