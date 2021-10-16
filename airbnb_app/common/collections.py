from typing import NamedTuple, Optional

from pydantic import BaseModel

from .types import AbstractForm, AbstractModel


class FormWithModel(NamedTuple):
    form: AbstractForm
    model: AbstractModel


class TwilioShortPayload(BaseModel):
    status: str
    sid: Optional[str]
