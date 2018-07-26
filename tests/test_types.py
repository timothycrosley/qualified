import pytest

from qualified.types import string_boolean


def test_string_boolean():
    assert string_boolean('f') == False
    assert string_boolean('t') == True
    assert string_boolean('False') == False
    assert string_boolean('True') == True
    assert string_boolean('0') == False
    assert string_boolean('1') == True
    assert string_boolean('10') == True
    assert string_boolean('') == False
    assert string_boolean('Anything Else') == True
    
    with pytest.raises(AttributeError):
        string_boolean({'Not': 'a string'})
