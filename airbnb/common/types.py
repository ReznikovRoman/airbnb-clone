from typing import Type, TypeVar

from django.forms.forms import BaseForm


FORM = TypeVar('FORM', bound=Type[BaseForm])
