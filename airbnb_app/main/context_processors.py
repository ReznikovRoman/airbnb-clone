from typing import Dict

from django.http import HttpRequest


def absolute_url(request: HttpRequest) -> Dict[str, str]:
    urls = {
        'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip('/'),
        'ABSOLUTE_URL': request.build_absolute_uri(),
    }
    return urls
