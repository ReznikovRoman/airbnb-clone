#!/bin/bash
source ./src/.env

function create_cloud_function {
    yc serverless function create \
      --name="$YANDEX_FUNCTION_NAME" \
      --cloud-id="$YANDEX_CLOUD_ID" \
      --folder-id="$YANDEX_FOLDER_ID"
}

function create_cloud_function_version {
  yc serverless function version create \
    --function-name="$YANDEX_FUNCTION_NAME" \
    --service-account-id="$YANDEX_SERVICE_ACCOUNT_ID" \
    --cloud-id="$YANDEX_CLOUD_ID" \
    --folder-id="$YANDEX_FOLDER_ID" \
    --runtime python39 \
    --entrypoint main.handler \
    --memory 128m \
    --execution-timeout 30s \
    --source-path ./build.zip \
    --environment YANDEX_AWS_ACCESS_KEY_ID="$YANDEX_AWS_ACCESS_KEY_ID",YANDEX_AWS_SECRET_ACCESS_KEY="$YANDEX_AWS_ACCESS_KEY_SECRET",YANDEX_AWS_DEFAULT_REGION="$YANDEX_AWS_DEFAULT_REGION",YANDEX_IAM_TOKEN="$YANDEX_IAM_TOKEN",YANDEX_FOLDER_ID="$YANDEX_FOLDER_ID",YANDEX_FUNCTION_NAME="$YANDEX_FUNCTION_NAME",YANDEX_BUCKET_NAME="$YANDEX_BUCKET_NAME",RESIZE_IMAGE_VALID_SIZES="$RESIZE_IMAGE_VALID_SIZES"

  yc serverless function allow-unauthenticated-invoke \
    --name="$YANDEX_FUNCTION_NAME" \
    --cloud-id="$YANDEX_CLOUD_ID" \
    --folder-id="$YANDEX_FOLDER_ID"
}

function deploy {
  make check
  make compile-requirements
  python3 src/build.py
  create_cloud_function || create_cloud_function_version
}

echo "Deploying '$YANDEX_FUNCTION_NAME' function"
deploy
