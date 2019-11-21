import os
import io
import json
import logging
from flask import Flask, redirect, url_for, make_response, jsonify,  _request_ctx_stack
from flask.logging import default_handler
from oauth import AuthError, requires_auth
from pathlib import Path
from flask_cors import cross_origin


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
root = Path(__file__).absolute().parent

formatter = logging.Formatter(
    " %(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
default_handler.setFormatter(formatter)
default_handler.setLevel(logging.INFO)

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    print('handling error')
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# Controllers API

# This doesn't need authentication
@app.route("/public")
@cross_origin(headers=['Content-Type', 'Authorization'])
def public():
    response = "Public endpoint - open to all"
    return jsonify(message=response)

# This needs authentication
@app.route("/api/user")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def private():
    return jsonify(message=_request_ctx_stack.top.current_user)

@app.route("/api/data")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def data():
    json_data = {
        "people": [
            {
                "id": 1,
                "name": "Josh",
                "age": 47
            },
            {
                "id": 2,
                "name": "Adam",
                "age": 45
            },
            {
                "id": 3,
                "name": "Fred",
                "age": 33
            },
            {
                "id": 4,
                "name": "Danny",
                "age": 53
            }
        ]
    }

    si = io.StringIO()
    json.dump(json_data, si)
    resp = make_response(si.getvalue())
    resp.headers['Content-Type'] = 'application/json'
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
