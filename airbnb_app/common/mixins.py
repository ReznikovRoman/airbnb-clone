from typing import List, Tuple, Union

from django.http import HttpRequest, HttpResponseRedirect


class SessionDataRequiredMixin:
    """Verify that there is all 'required_data' in the session, otherwise redirect to the 'redirect_url'."""

    required_session_data: Union[List[str], Tuple[str, ...]] = None
    redirect_url: str = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.required_session_data and \
                not all(required_data in request.session for required_data in self.required_session_data):
            return HttpResponseRedirect(self.redirect_url)
        return super(SessionDataRequiredMixin, self).dispatch(request, *args, **kwargs)
