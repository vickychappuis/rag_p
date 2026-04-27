import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

if os.environ.get("USE_SSM", "false").lower() == "true":
    import boto3

    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    paginator = ssm.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path="/promtior/", WithDecryption=True):
        for param in page["Parameters"]:
            key = param["Name"].split("/")[-1].upper()
            os.environ[key] = param["Value"]
