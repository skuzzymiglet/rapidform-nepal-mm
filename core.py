import json
import math
import statistics

def overall_confidence(data):
    text = data["fullTextAnnotation"]
    values = []
    for p in text["pages"]:
        for b in p["blocks"]:
            values.append(float(b["confidence"]))
    return statistics.mean(values)

def scan():
    pass

def parse(sample):
    pass
