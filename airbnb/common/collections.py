from typing import NamedTuple

from .types import AbstractForm, AbstractModel


class FormWithModel(NamedTuple):
    form: AbstractForm
    model: AbstractModel
