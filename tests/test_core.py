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
    expect = {
        "firstName": "ALIX",
        "lastName": "EMDEN",
        "gender": "female",
        "nationality": "USA",
        "dateOfBirth": "01/01/1990",
        "passportNumber": 1234567,
        "homeAddress": "123 USA, USA",
        "nepalAddress": "123 KATHAMANDU",
        "nepalPhone": {
            "mobile": "",
            "landline": "",
            "all": "123 456 7891"
        },
        "email": "emden@test.org"
        "journey": [
            {"from": "USA", "to": "NEPAL"},
            {"from": "", "to": ""},
            {"from": "", "to": ""}
        ],
        "contact": {
            "acute14": "true",
            "cared": "false",
            "funeral": "false",
            "visited": "false"
        },
        "health": {
            "fever": "false",
            "respiratory": "true",
            "temparature": "false",
            "headache": "true",
            "vomiting": "false",
            "diarrhoea": "false",
            "fatigue": "false",
            "bruising": "false",
            "bleeding": "false"
        },
        "flightNumber": ""
    }
    assert parse(sample) == expect
