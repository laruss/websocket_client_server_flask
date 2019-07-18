# "status" can be "","completed","failed"
import json
from time import sleep

JSON_NAME = 'assembly.json'

def open_json():
    _dict = {}
    with open(JSON_NAME) as file:
        _dict = json.load(file)
    return _dict

def save_json(json_dict):
    with open(JSON_NAME, 'w') as file:
        json.dump(json_dict, file)