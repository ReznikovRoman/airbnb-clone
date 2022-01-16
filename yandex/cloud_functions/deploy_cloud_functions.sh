#!/bin/bash
# Deploy all Yandex Cloud Functions
source .env

function export_envs {
  set -a
  source .env
  set +a
}

export_envs

echo "Deploy Cloud Functions"

yc config set token "$YANDEX_CLOUD_FUNCTIONS_OAUTH_TOKEN"

for dir in */; do
  cd "${dir}" || exit
  chmod +x ./deploy.sh
  ./deploy.sh
  cd ../
done
