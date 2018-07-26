"""Tests the Python3 implementation of qualified"""
import pytest

from qualified.schema import Schema, read_construct, construct, read_validator, validator

TEST_SCHEMA = """
__schema_name__: test_schema
name!: str!
age: int
height?: int
"""

def test_read_construct():
    assert read_construct('name') == construct(name='name', compute_quality=True, weight=1, required=False,
                                                    multiple=False)
    assert read_construct('name!') == construct(name='name', compute_quality=True, weight=1, required=True,
                                                     multiple=False)
    assert read_construct('name?') == construct(name='name', compute_quality=False, weight=0, required=False,
                                                     multiple=False)
    assert read_construct('name+') == construct(name='name', compute_quality=True, weight=1, required=False,
                                                     multiple=True)
    assert read_construct('name~1.5') == construct(name='name', compute_quality=True, weight=1.5, required=False,
                                                        multiple=False)
    assert read_construct('name!+~1.5') == construct(name='name', compute_quality=True, weight=1.5, required=True,
                                                        multiple=True)
    assert read_construct('name?!|?') == construct(name='name?!', compute_quality=False, weight=0, required=False,
                                                        multiple=False)
    
    
    with pytest.raises(ValueError):  # You cannot specify a non numeric quality score
        read_construct('name?~a')
    with pytest.raises(ValueError):  # You cannot specify a fully optional field with a quality weight
        read_construct('name?~1.5')
    
    # You cannot specify any modifier twice
    with pytest.raises(ValueError):
        read_construct('name++')
    with pytest.raises(ValueError):
        read_construct('name??')
    with pytest.raises(ValueError):
        read_construct('name!!')

        
def test_read_validator():
    assert read_validator('int! 1 min=10:int max=10 max=20') == validator(construct(name='int', compute_quality=True,
                                                                                    weight=1, required=True,
                                                                                    multiple=False),
                                                                    args=['1'], kwargs={'min': 10, 'max': ['10', '20']})
    
    with pytest.raises(ValueError):
        read_validator('int min=10:not_a_type')
        
        
        
def test_schema():
    schema = Schema(definition=TEST_SCHEMA)
    assert schema.qualify({'name': 'Timothy', 'age': 28}) == {'name': 'Timothy', 'age': 28, 'schema': 'test_schema',
                                                              'quality': 1.0}
    assert schema.qualify({'name': 'Timothy', 'age': 28}) == {'name': 'Timothy', 'schema': 'test_schema',
                                                              'quality': 0.5}
    
    
