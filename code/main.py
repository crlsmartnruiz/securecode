import json
import os
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
from openai import OpenAI
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
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return get_secret_value_response["SecretString"]


def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") else json.loads(get_secret("openai-key")).get("apiKey")


def call_openai_api(prompt: str) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return completion.choices[0].message.content


app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        return jsonify({"response": call_openai_api(user_message)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    app.logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

if __name__ == "__main__":
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000))
