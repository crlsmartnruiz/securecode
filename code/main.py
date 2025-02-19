import json
import os
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
from time import strftime
import logging
from logging.handlers import RotatingFileHandler


def get_secret(secret_name: str):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name="eu-west-2"
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        raise e

    return get_secret_value_response["SecretString"]


app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def index():
    secret_name = "prod/clave-prueba" if os.getenv("ENVIRONMENT", "dev") == "prod" else "dev/clave-prueba"
    return jsonify({"key": get_secret(secret_name)})


@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    app.logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr,
                     request.method, request.scheme, request.full_path, response.status)
    return response


if __name__ == "__main__":
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000))
