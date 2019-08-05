# "status" can be "","completed","failed"
import json
from time import sleep

JSON_NAME = 'assembly.json'
NO_CLIENTS = False
SECS_TO_PING = 5
SECS_TO_FAIL_RESPONSE = 1000

def open_json():
    _dict = {}
    with open(JSON_NAME) as file:
        _dict = json.load(file)
    return _dict

def save_json(json_dict):
    with open(JSON_NAME, 'w') as file:
        json.dump(json_dict, file)