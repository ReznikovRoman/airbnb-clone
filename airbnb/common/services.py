from typing import List

from .types import FORM


def get_field_names_from_form(form: FORM) -> List[str]:
    return list(form.base_fields.keys())
