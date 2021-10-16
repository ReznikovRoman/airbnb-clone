from typing import Type, TypeVar

from django.http import HttpRequest
from django.forms import BaseForm
from django.db.models import Model

from accounts.models import CustomUser


AbstractForm = TypeVar('AbstractForm', bound=Type[BaseForm])

AbstractModel = TypeVar('AbstractModel', bound=Type[Model])


class AuthenticatedHttpRequest(HttpRequest):
    user: CustomUser
