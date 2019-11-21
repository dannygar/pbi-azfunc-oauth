# from flask import Flask
# app = Flask(__name__)
# @app.route("/api")
# def hello():
#     print('******************* route hit')
#     return "Hello, Flask!"

# if __name__ == "secureFlaskApp":
#     print('******************* init')
#     app.run()


import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from jose import jwt
from pathlib import Path
app = Flask(__name__)
root = Path(__file__).absolute().parent

API_AUDIENCE = "https://pyfuncapi.microsoft.onmicrosoft.com"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"

# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    print('handling error')
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# Format error response and append status code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            jsonurl = urlopen("https://login.microsoftonline.com/" +
                            TENANT_ID + "/discovery/v2.0/keys")
            jwks = json.loads(jsonurl.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
        except Exception:
            raise AuthError({"code": "invalid_header",
                                "description":
                                "Unable to parse authentication"
                                " token."}, 401)
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=API_AUDIENCE,
                    issuer="https://sts.windows.net/" + TENANT_ID + "/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                 "incorrect claims,"
                                 "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                 "Unable to parse authentication"
                                 " token."}, 401)
            _request_ctx_stack.top.current_user = payload
            # print(_request_ctx_stack.top.current_user)
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False

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
    with open(root / 'sample.dat') as sample_data:
        result = json.load(sample_data)
        return result

if __name__ == '__main__':
    app.run()
