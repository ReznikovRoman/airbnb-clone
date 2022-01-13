import os
from enum import Enum
from typing import Final, TypedDict

import boto3
import requests
from botocore.config import Config
from dotenv import load_dotenv


load_dotenv()


YANDEX_AWS_ACCESS_KEY_ID: Final[str] = os.getenv("YANDEX_CLOUD_FUNCTIONS_AWS_ACCESS_KEY_ID")
YANDEX_AWS_ACCESS_KEY_SECRET: Final[str] = os.getenv("YANDEX_CLOUD_FUNCTIONS_AWS_ACCESS_KEY_SECRET")
YANDEX_AWS_DEFAULT_REGION: Final[str] = os.getenv("YANDEX_CLOUD_FUNCTIONS_AWS_DEFAULT_REGION")
YANDEX_IAM_TOKEN: Final[str] = os.getenv("YANDEX_FUNCTION_RESIZE_IMAGE_IAM_TOKEN")
YANDEX_FOLDER_ID: Final[str] = os.getenv("YANDEX_FUNCTION_RESIZE_IMAGE_FOLDER_ID")
YANDEX_FUNCTION_NAME: Final[str] = os.getenv("YANDEX_FUNCTION_RESIZE_IMAGE_NAME")
YANDEX_BUCKET_NAME: Final[str] = os.getenv("YANDEX_FUNCTION_RESIZE_IMAGE_BUCKET_NAME")


class YandexFunctionListInfo(TypedDict):
    id: str
    folderId: str  # noqa: N815
    createdAt: str  # noqa: N815
    name: str
    description: str
    logGroupId: str  # noqa: N815
    httpInvokeUrl: str  # noqa: N815
    status: str


class YandexFunctionNotFoundError(Exception):

    def __init__(self, function_name: str):
        self.function_name = function_name

    def __str__(self):
        return f"Function `{self.function_name}` was not found."


class YandexCloudAPIUrl(Enum):
    SERVERLESS_FUNCTIONS_LIST = "https://serverless-functions.api.cloud.yandex.net/functions/v1/functions"


def get_cloud_function_id_by_name(
        folder_id: str,
        function_name: str,
        iam_token: str,
) -> str:
    # HTTP requests params: https://cloud.yandex.ru/docs/functions/functions/api-ref/Function/list#https-request
    url = f'{YandexCloudAPIUrl.SERVERLESS_FUNCTIONS_LIST.value}?folder_id={folder_id}&filter=name="{function_name}"'
    response = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {iam_token}",
        },
    ).json()
    if not response:
        raise YandexFunctionNotFoundError(function_name=function_name)
    function_data: YandexFunctionListInfo = response["functions"][0]
    return function_data['id']


def get_s3_client():
    s3_config = Config(
        region_name=YANDEX_AWS_DEFAULT_REGION,
    )
    session = boto3.session.Session()
    client = session.client(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=YANDEX_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=YANDEX_AWS_ACCESS_KEY_SECRET,
        config=s3_config,
    )
    return client


def configure_routes() -> None:
    client = get_s3_client()
    function_id = get_cloud_function_id_by_name(
        folder_id=YANDEX_FOLDER_ID,
        function_name=YANDEX_FUNCTION_NAME,
        iam_token=YANDEX_IAM_TOKEN,
    )
    client.put_bucket_website(
        Bucket=YANDEX_BUCKET_NAME,
        WebsiteConfiguration={
            'IndexDocument': {
                'Suffix': 'index.html',
            },
            'RoutingRules': [
                {
                    'Condition': {
                        'HttpErrorCodeReturnedEquals': '404',
                        'KeyPrefixEquals': 'resized/',
                    },
                    'Redirect': {
                        'HostName': 'functions.yandexcloud.net',
                        'HttpRedirectCode': '302',
                        'Protocol': 'https',
                        'ReplaceKeyPrefixWith': f"{function_id}?path=",
                    },
                },
            ],
        },
    )


def get_bucket_config() -> None:
    client = get_s3_client()
    response = client.get_bucket_website(Bucket=YANDEX_BUCKET_NAME)
    print(response)


if __name__ == '__main__':
    configure_routes()
    get_bucket_config()
