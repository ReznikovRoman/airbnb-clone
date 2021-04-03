from typing import Type, TypeVar

from django.forms.forms import BaseForm


Form = TypeVar('Form', bound=Type[BaseForm])
