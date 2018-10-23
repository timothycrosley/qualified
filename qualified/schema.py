import yaml
import json
import requests
from collections import namedtuple
from qualified.types import string_boolean

construct = namedtuple('Construct', ['name', 'compute_quality', 'weight', 'required', 'multiple'])
validator = namedtuple('Validator', ['construct', 'args', 'kwargs'])
SUPPORTED_TYPES = {'str': str, 'int': int, 'bool': string_boolean, 'float': float}


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


def _read_value(value, supported_types):
    if ':' in value:
        value, value_type = value.split(':')
        if not value_type in supported_types:
            raise ValueError('provided type of "{}" not one of the support value types: {}'.format
                                (value_type, ', '.join(supported_types.keys())))
        return supported_types[value_type](value)

    return value


def read_validator(string, supported_types=SUPPORTED_TYPES):
    parts = string.split(' ')
    kind = read_construct(parts.pop(0))

    args = []
    kwargs = {}
    for value in parts:
        if '=' in value:
            key, value = value.split('=')
            value = _read_value(value, supported_types)

            if key in kwargs:
                if kwargs[key] != list:
                    kwargs[key] = [kwargs[key]]
                kwargs[key].append(value)
            else:
                kwargs[key] = value
        else:
            args.append(_read_value(value, supported_types))

    return validator(kind, args, kwargs)


def compile_validators(field, validators, supported_types, fail_fast=False):
    code = ['possible_validator_score = 0',
            'validator_score = 0']

    field = read_construct(field)
    for validator in validators:

        validator = read_validator(validator, supported_types=supported_types)
        if validator.construct.weight:
            code.append('possible_validator_score += {}'.format(validator.construct.weight))
        code.append('try:')
        code.append('    value = {}(value, *{}, **{})'.format(validator.construct.name, repr(validator.args),
                                                              repr(validator.kwargs)))
        if validator.construct.weight:
            code.append('    validator_score += {}'.format(validator.construct.weight))
        code.append('except Exception as e:')
        if validator.construct.required or field.required:
            if fail_fast:
                code.append('    raise e')
            else:
                code.append('    errors.append(e)')
        else:
            code.append('    pass')
    return code


def compile_schema(schema, supported_types=SUPPORTED_TYPES):
    compiled = []
    for key, validators in schema:
        key = read_construct(key)
        if type(validators) == dict:
            compile_schema(validators)
        elif type(validators) == str:
            validators = [validators]


        for validator in validators:
            validator = read_validator(validator)
            compiled.append('try:')
            compiled.append('    value = {}(input["{}"])')



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
        code = ['score = 0',
                'possible_score = 0',
                'output = {}']

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

