# test_setup.py
import os
import boto3
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check Python version
python_version = sys.version_info
required_version = (3, 12)

print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major < required_version[0] or (python_version.major == required_version[0] and python_version.minor < required_version[1]):
    print(f"WARNING: Python {required_version[0]}.{required_version[1]} or higher is required for this workshop.")
    print(f"Your version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("Please upgrade your Python version before proceeding.")
else:
    print(f"Python version check passed! You have {python_version.major}.{python_version.minor}.{python_version.micro}")

# Check if AWS credentials are available
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

if aws_access_key and aws_secret_key and aws_region:
    print("AWS credentials found!")
    print(f"Region: {aws_region}")
    
    # Try to get AWS account information
    try:
        sts_client = boto3.client('sts')
        account_info = sts_client.get_caller_identity()
        print(f"Successfully connected to AWS!")
        print(f"Account ID: {account_info['Account']}")
        print(f"User ARN: {account_info['Arn']}")
    except Exception as e:
        print(f"Error connecting to AWS: {e}")
else:
    print("AWS credentials missing. Please check your .env file.")
