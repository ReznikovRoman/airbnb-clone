from storages.backends.s3boto3 import S3Boto3Storage

from django.conf import settings


class YandexObjectMediaStorage(S3Boto3Storage):
    bucket_name = settings.YANDEX_STORAGE_BUCKET_NAME
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
