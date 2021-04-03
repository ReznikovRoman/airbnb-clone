from typing import Type, TypeVar

from django.forms import BaseForm
from django.db.models import Model


AbstractForm = TypeVar('AbstractForm', bound=Type[BaseForm])

AbstractModel = TypeVar('AbstractModel', bound=Type[Model])
