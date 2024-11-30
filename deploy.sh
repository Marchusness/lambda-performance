#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create a Lambda zip file
create_lambda_zip() {
    local file_name=$1
    local zip_name="${file_name%.*}.zip"
    echo "Creating $zip_name..."
    if [ -f "$file_name" ]; then
        zip -j "$zip_name" "$file_name"
    else
        echo "Error: $file_name not found"
        exit 1
    fi
}

# Check if required commands are available
if ! command_exists terraform; then
    echo "Error: terraform is not installed. Please install it and try again."
    exit 1
fi

if ! command_exists aws; then
    echo "Error: aws CLI is not installed. Please install it and try again."
    exit 1
fi

if ! command_exists zip; then
    echo "Error: zip is not installed. Please install it and try again."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "Error: AWS credentials are not configured. Please run 'aws configure' and try again."
    exit 1
fi

# Check if required Python files exist
required_files=(
    "lambda_orchestrator.py"
    "lambda_downloader.py"
    "hello_world_lambda.py"
    "lambda_invoke_other_lambdas_orchestrator.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found"
        exit 1
    fi
done

# Clean up any existing zip files
echo "Cleaning up existing ZIP files..."
rm -f *.zip

# Create ZIP files for Lambda functions
echo "Creating ZIP files for Lambda functions..."
create_lambda_zip "lambda_orchestrator.py"
create_lambda_zip "lambda_downloader.py"
create_lambda_zip "hello_world_lambda.py"
create_lambda_zip "lambda_invoke_other_lambdas_orchestrator.py"

# Install required Python packages for the orchestrator
echo "Installing Python dependencies..."
pip install \
    'urllib3<2.0.0' \
    'aioboto3==9.3.1' \
    'aiohttp>=3.7.0,<3.9.0' \
    'typing_extensions>=4.0.0' \
    'aiohttp-retry>=2.8.3' \
    -t ./package
cd package
zip -r9 ../lambda_invoke_other_lambdas_orchestrator.zip .
cd ..
zip -g lambda_invoke_other_lambdas_orchestrator.zip lambda_invoke_other_lambdas_orchestrator.py
rm -rf package

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Apply Terraform changes directly
echo "Applying Terraform changes..."
terraform apply -auto-approve

# Clean up
echo "Cleaning up..."
rm -f *.zip tfplan

echo "Deployment completed successfully!"
