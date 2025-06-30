import os
import json
import boto3
from typing import Dict, Any
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()  # optional, only if using .env files

# Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-west-1")
MODEL_ID = os.getenv("TEXT_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")

# Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=Config(
    read_timeout=300,
    connect_timeout=300,
    retries={"max_attempts": 3}
))


def call_bedrock(prompt: str) -> str:
    """Call Bedrock Claude model with a user prompt and return the completion text."""

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.5,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    response_body = response["body"].read().decode("utf-8")
    response_data = json.loads(response_body)

    # Claude 3 returns list of content parts
    if "content" in response_data:
        return "".join(part["text"] for part in response_data["content"] if "text" in part)

    return "No content returned from LLM"
import os
import json
import boto3
from typing import Dict, Any
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()  # optional, only if using .env files

# Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-west-1")
MODEL_ID = os.getenv("TEXT_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")

# Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=Config(
    read_timeout=300,
    connect_timeout=300,
    retries={"max_attempts": 3}
))


def call_bedrock(prompt: str) -> str:
    """Call Bedrock Claude model with a user prompt and return the completion text."""

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.5,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    response_body = response["body"].read().decode("utf-8")
    response_data = json.loads(response_body)

    # Claude 3 returns list of content parts
    if "content" in response_data:
        return "".join(part["text"] for part in response_data["content"] if "text" in part)

    return "No content returned from LLM"
