from __future__ import annotations

import base64
import os
import re
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING, Any, Callable, Final, NamedTuple, TypedDict, Union

import boto3
from botocore.config import Config
from PIL import Image


if TYPE_CHECKING:
    milliseconds = str
    seconds = str

    class RequestContextIdentity(TypedDict):
        sourceIp: str  # noqa: N815
        userAgent: str  # noqa: N815

    class RequestContext(TypedDict):
        identity: RequestContextIdentity
        httpMethod: str  # noqa: N815
        requestId: str  # noqa: N815
        requestTime: str  # noqa: N815
        requestTimeEpoch: int  # noqa: N815

    class HttpEvent(TypedDict):
        httpMethod: str  # noqa: N815
        headers: dict[str, str]
        path: str
        multiValueHeaders: dict[str, list[str]]  # noqa: N815
        queryStringParameters: dict[str, str]  # noqa: N815
        multiValueQueryStringParameters: dict[str, list[str]]  # noqa: N815
        requestContext: RequestContext  # noqa: N815
        body: str
        isBase64Encoded: bool  # noqa: N815

    # HttpEvent: https://cloud.yandex.com/en-ru/docs/functions/concepts/function-invoke#http
    Event = Union[dict[Any, Any], HttpEvent]

    class TokenInfo(TypedDict):
        # IAM token
        access_token: str

        # token lifetime (in seconds)
        expires_in: seconds

        # token type (Bearer)
        token_type: str

    @dataclass
    class Context:
        # function's identifier
        function_name: str

        # function's version identifier
        function_version: str

        # function's memory limit
        memory_limit_in_mb: str

        # request's identifier
        request_id: str

        # parameters required for authentication in Yandex.Cloud API
        token: TokenInfo

        # returns the time (in ms), remaining to complete the current request
        get_remaining_time_in_millis: Callable[..., milliseconds]


VALID_EXTENSIONS: Final[tuple[str, ...]] = (
    "jpeg",
    "jpg",
    "png",
)
PILLOW_IMAGE_CONVERSATION_REQUIRED_MODS: Final[tuple[str, ...]] = (
    "RGBA",
    "P",
)
PILLOW_IMAGE_DEFAULT_FORMAT: Final[str] = "jpeg"
PILLOW_RESIZE_IMAGE_WIDTH: Final[int] = 500
PILLOW_RESIZE_IMAGE_HEIGHT: Final[int] = 500


class FileInfo(NamedTuple):
    target_object_key: str
    initial_object_key: str
    target_width: int
    target_height: int
    filename: str


YANDEX_OBJECT_STORAGE_MEDIA_PREFIX: Final[str] = os.environ.get("YANDEX_OBJECT_STORAGE_MEDIA_PREFIX")
YANDEX_OBJECT_STORAGE_BUCKET: Final[str] = os.environ.get("YANDEX_OBJECT_STORAGE_BUCKET")
YANDEX_AWS_ACCESS_KEY_ID: Final[str] = os.environ.get("YANDEX_AWS_ACCESS_KEY_ID")
YANDEX_AWS_SECRET_ACCESS_KEY: Final[str] = os.environ.get("YANDEX_AWS_SECRET_ACCESS_KEY")
YANDEX_AWS_DEFAULT_REGION: Final[str] = os.environ.get("YANDEX_AWS_DEFAULT_REGION")


def parse_object_key(*, object_key: str = "images/realty/1/300x300/flat_1.jpg") -> FileInfo:
    groups = re.search(r'((\d+)x(\d+))/(.*)', object_key).groups()
    file_info = FileInfo(
        target_object_key=object_key,
        initial_object_key=object_key.replace(f"{groups[0]}/", ""),
        target_width=int(groups[1]),
        target_height=int(groups[2]),
        filename=groups[3],
    )
    return file_info


def resize_image(*, file_info: FileInfo) -> dict[str, Any] | None:
    bucket_name = YANDEX_OBJECT_STORAGE_BUCKET
    s3_config = Config(
        region_name=YANDEX_AWS_DEFAULT_REGION,
    )

    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=YANDEX_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=YANDEX_AWS_SECRET_ACCESS_KEY,
        config=s3_config,
    )

    file_extension = file_info.filename.rsplit(".")[-1].lower()
    if file_extension not in VALID_EXTENSIONS:
        return

    object_response = s3.get_object(
        Bucket=bucket_name,
        Key=file_info.initial_object_key,
    )
    object_body = object_response['Body'].read()
    image = Image.open(BytesIO(object_body))
    image.thumbnail(size=(file_info.target_width, file_info.target_height))
    with BytesIO() as buffer:
        if image.mode in PILLOW_IMAGE_CONVERSATION_REQUIRED_MODS:
            image = image.convert("RGB")
        image.save(buffer, PILLOW_IMAGE_DEFAULT_FORMAT)
        buffer.seek(0)
        s3.put_object(
            Bucket=bucket_name,
            Key=file_info.target_object_key,
            Body=buffer,
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "image/jpeg",
            },
            "isBase64Encoded": True,
            "body": base64.b64encode(buffer.getvalue()).decode(),
        }


def handler(event: HttpEvent, context: Context):
    """Handles image resizing requests.

    Handler arguments:
    - https://cloud.yandex.com/en-ru/docs/functions/lang/python/handler
    - https://cloud.yandex.com/en-ru/docs/functions/lang/python/context
    """
    try:
        path: str = event['queryStringParameters']['path']
    except KeyError:
        return

    object_key = f"{YANDEX_OBJECT_STORAGE_MEDIA_PREFIX}{path}"
    response = resize_image(
        file_info=parse_object_key(object_key=object_key),
    )

    return response
