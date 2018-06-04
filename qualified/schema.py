import yaml
import json
import requests
from collections import namedtuple

construct = namedtuple('Construct', ['name', 'compute_quality', 'weight', 'required', 'multiple'])


def read_construct(line):
    if '~' in line:
        split_line = line.split('~', -1)
        weight = split_line.pop(-1)
        try:
            weight = float(weight)
        except ValueError:
            raise ValueError('Weight must be a float value not "{}"'.format(weight))
        line = '~'.join(split_line)
    else:
        weight = 1

    required = False
    compute_quality = True
    multiple = False
    for index, character in enumerate(line[::-1]):
        if character == '!':
            if required:
                raise ValueError('You cannot set required twice!')
            required = True
        elif character == '?':
            if not compute_quality:
                raise ValueError('You cannot unset quality computations twice!')
            elif weight != 1:
                raise ValueError('You cannot set a quality weight but then specify to skip quality')
            compute_quality = False
            weight = 0
        elif character == '+':
            if multiple:
                raise ValueError('You cannot set multiple twice!')
            multiple = True
        elif character == '|':
            index += 1
            break
        else:
            break
        
    return construct(line[:-index] if index else line, compute_quality, weight, required, multiple)


class Schema(object):
    
    def __init__(self, definition=None, filename=None, url=None, serializer=json):
        sources = list(filter(bool, (filename, url,  definition)))
        if not sources:
            raise ValueError("A schema filename, url, or definition must be defined")
        elif len(sources) > 1:
            raise ValueError("You cannot specify multile sources. Choose one: filename, url, or definition.")
        
        if url:
            definition = requests.get(url).content
        elif filename:
            with open(filename) as schema_file:
                definition = schema_file.read()
        
        self.definition = yaml.load(definition)
        self.name = self.definition.pop('__schema_name__', '')
        self.version = self.definition.pop('__schema_version__', '')
        


    def compile(self):
        code = []
        for name, value in self.definition.items():
            required = False
            compute_quality = True
            weight = 1
            name, score = name.split('~')
            
            if '!' in name:
                name = name.replace('!', '')
                required = True
            if '?' in name:
                name = name.replace('?', '')
                compute_quality = False
            
                
                
                
                
                
            code += 'try:'
            code += '   value = {}(value)'
        
