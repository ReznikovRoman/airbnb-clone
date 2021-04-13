from django.http import HttpRequest
from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect, reverse

from .models import Subscriber
from .forms import SubscriberEmailForm
from .services import get_subscriber_by_user


class SubscribeView(generic.View):
    """View for handling new subscriptions."""
    def post(self, request: HttpRequest, *args, **kwargs):
        subscription_form = SubscriberEmailForm(request.POST)

        if subscription_form.is_valid():
            new_subscriber: Subscriber = subscription_form.save(commit=False)

            # if user is authenticated and not subscribed
            if request.user.is_authenticated and \
                    not get_subscriber_by_user(user=request.user).exists():
                new_subscriber.user = request.user

            new_subscriber.save()

            messages.add_message(request, messages.SUCCESS, message='You have successfully subscribed.')
        else:
            messages.add_message(request, messages.ERROR, message='There was an error while trying to subscribe.')

        return redirect(request.META.get('HTTP_REFERER', reverse('home_page')))
