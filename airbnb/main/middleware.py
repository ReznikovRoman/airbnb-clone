import re

from django.http import HttpRequest, HttpResponse


class MobileUserAgentMiddleware:
    """Middleware for checking whether the request comes from a mobile device."""
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request: HttpRequest, *args, **kwargs):
        mobile_agent_regex = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

        request.is_mobile_agent = False
        if mobile_agent_regex.match(request.META['HTTP_USER_AGENT']):
            request.is_mobile_agent = True

        response: HttpResponse = self._get_response(request)
        return response
