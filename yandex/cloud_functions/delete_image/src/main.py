from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Final, NamedTuple, TypedDict, Union

import boto3
from botocore.config import Config


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

    class TracingContext(TypedDict):
        trace_id: str
        span_id: str
        parent_span_id: str

    class EventMetadata(TypedDict):
        event_id: str
        event_type: str
        created_at: str
        tracing_context: TracingContext
        cloud_id: str
        folder_id: str

    class EventDetails(TypedDict):
        bucket_id: str
        object_id: str

    class ObjectStorageEventMessage(TypedDict):
        event_metadata: EventMetadata
        details: EventDetails

    class ObjectStorageEvent(TypedDict):
        messages: list[ObjectStorageEventMessage]

    # HttpEvent: https://cloud.yandex.com/en-ru/docs/functions/concepts/function-invoke#http
    # TriggerEvent: https://cloud.yandex.ru/en-ru/docs/functions/concepts/trigger/os-trigger#ymq-format
    Event = Union[dict[Any, Any], ObjectStorageEvent, HttpEvent]

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


YANDEX_OBJECT_STORAGE_MEDIA_RESIZED_PREFIX: Final[str] = os.environ.get(
    key="YANDEX_FUNCTION_DELETE_IMAGE_OBJECT_STORAGE_MEDIA_RESIZED_PREFIX",
    default="resized/",
)
YANDEX_OBJECT_STORAGE_MEDIA_PREFIX: Final[str] = os.environ.get(
    key="YANDEX_FUNCTION_DELETE_IMAGE_OBJECT_STORAGE_MEDIA_PREFIX",
    default="media/",
)
YANDEX_OBJECT_STORAGE_BUCKET: Final[str] = os.environ.get("YANDEX_FUNCTION_DELETE_IMAGE_BUCKET_NAME")
YANDEX_AWS_ACCESS_KEY_ID: Final[str] = os.environ.get("YANDEX_CLOUD_FUNCTIONS_AWS_ACCESS_KEY_ID")
YANDEX_AWS_SECRET_ACCESS_KEY: Final[str] = os.environ.get("YANDEX_CLOUD_FUNCTIONS_AWS_ACCESS_KEY_SECRET")
YANDEX_AWS_DEFAULT_REGION: Final[str] = os.environ.get("YANDEX_CLOUD_FUNCTIONS_AWS_DEFAULT_REGION")


class FileInfo(NamedTuple):
    initial_object_key: str
    base_filepath: str
    filename: str


def parse_object_key(*, object_key: str) -> FileInfo:
    base_filepath, filename = object_key.rsplit("/", 1)
    base_filepath = (
        base_filepath.replace(YANDEX_OBJECT_STORAGE_MEDIA_PREFIX, YANDEX_OBJECT_STORAGE_MEDIA_RESIZED_PREFIX, 1)
    )
    file_info = FileInfo(
        initial_object_key=object_key,
        base_filepath=f"{base_filepath}/",
        filename=filename,
    )
    return file_info


def delete_resized_image(*, file_info: FileInfo) -> None:
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
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=file_info.base_filepath)
    objects = response.get("Contents", [])
    objects_to_delete = [
        {'Key': s3_object['Key']}
        for s3_object in objects
        if s3_object['Key'].endswith(file_info.filename) and s3_object['Key'] != file_info.initial_object_key
    ]
    if len(objects_to_delete) > 0:
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})


def handler(event: ObjectStorageEvent, context: Context) -> dict[str, Any]:
    """Delete resized images on initial image deletion.

    Handler arguments:
    - https://cloud.yandex.com/en-ru/docs/functions/lang/python/handler
    - https://cloud.yandex.com/en-ru/docs/functions/lang/python/context
    """
    try:
        messages = event['messages']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Error: `Event` must contain `messages` list.',
            }),
        }
    for message in messages:
        try:
            object_id = message['details']['object_id']
        except KeyError:
            continue
        delete_resized_image(
            file_info=parse_object_key(object_key=object_id),
        )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': "Resized images have been deleted.",
        }),
    }
