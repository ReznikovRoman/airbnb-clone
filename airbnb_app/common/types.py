from typing import Type, TypeVar

from django.db.models import Model
from django.forms import BaseForm
from django.http import HttpRequest

from accounts.models import CustomUser


seconds = int

AbstractForm = TypeVar('AbstractForm', bound=Type[BaseForm])

AbstractModel = TypeVar('AbstractModel', bound=Type[Model])


class AuthenticatedHttpRequest(HttpRequest):
    user: CustomUser
