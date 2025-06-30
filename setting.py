import os
fron typing inport Dict ,Any
from dotenv import load_dotenv
from botocore.config import config
import boto3 
import json

Bedrock_clinet_config = {
    "region_name": os.getnenv("Aws_region"),
}

Bedrock_code_model_config = {
    "model": os.getenv("code_model"),
    "temperature":0,
    "max_tokens": 60,
    "stop_sequence":["\n\nHuman:"]
}

Bedrock_text_model_config = {
    "model":os.getnev("Text_model"),
    "temperature":0.7,
    "max_tokens": 4096,
    "stop_sequence":["\n\nHuman:"]
    
    
}

Bedrock_LLM_Config = {
    "config_list": [{
        "model":"anthropic.cluade-3-5-sonnet-20240620-v1:0",
        "aws_region": "us-west-1",
        "api_type": "bedrock"}]
}

Aws_region = "us-west-1"
bedrock = botoe.client("bedrock-runtime",region_name=Aws_region)

model_id = "anthropoc.claude-3-sonnet"
config = config(
    read_timeout=300,
    connect_timeout=300)

def call_bedrock(prompt)
 bedrock = boto3.client("bedrock-runtime",region_name='us-west-1',config=config)
    model_id = "antropic.calude-3-5-sonnet-20240620-v1:0"
payload = {
    "anthropic_version":"bedrock-2023-05031",
    "messages": [
        {"role":"user":"content":prompt}
    ],
    "max_tokens":5000,
    "temperature":0,
    "top_p":0.1
}

reponse = bedrock.invoke_model(
    modeid = model_id,
    body = json.dumps(payload)
)
repsonse_body = response["body"].read().decode("utf-8")
repsonse_data= json.loads(response_body)

if "content" in response_data and response_data["content"]:
    answer =response_data["content"][0]["text"]
    return answer
}
