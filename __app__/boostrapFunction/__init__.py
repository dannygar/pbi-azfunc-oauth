import sys
import logging
import azure.functions as func

from azf_wsgi import AzureFunctionsWsgi
from . import secureFlaskApp as flaskApp

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return AzureFunctionsWsgi(flaskApp.app).main(req)