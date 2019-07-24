from flask import Flask, request, Response, jsonify
from settings import *
app = Flask(__name__)

@app.route("/")
def mainPage():
    return "This is a main page of webserver. Go to /start_tests/?assembly=<assembly_number> to run tests"

@app.route("/start_tests/", methods=['GET'])
def runTests():
    try:
        assemblyNum = request.args['assembly']
        resp = Response('success')
        try:
            result = get_tests_status(assemblyNum)
            print(result)
            if not result:
                resp = Response('failed', status=400)
        except Exception as e:
            print(e)
            resp = Response('There was an exception appeared while trying to run tests', status=400)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except KeyError:
        return mainPage()

def get_tests_status(assemblyNum):
    json_dict = open_json()
    if json_dict['no_clients']:
        return False
    json_dict.update({"assembly":assemblyNum})
    json_dict.update({'status':''})
    save_json(json_dict)

    not_finished = True
    while not_finished:
        sleep(1)
        check_status = open_json()
        if check_status['status'] in ("completed","failed"):
            not_finished = False
    print(check_status)
    if check_status['status'] == "completed":
        return True
    else:
        return False