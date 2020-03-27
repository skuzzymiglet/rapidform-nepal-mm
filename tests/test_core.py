import json
import pytest
from core import *

@pytest.fixture(scope="module")
def sample():
    file = open("tests/sample-gcv-response.json", "r")
    data = json.load(file)
    file.close()
    return data

def test_scan(sample):
    assert True

def test_overall_confidence(sample):
    assert overall_confidence(sample) == 0.9445454545454546

def test_parse(sample):
    expect = {}
    assert parse(sample) == expect
