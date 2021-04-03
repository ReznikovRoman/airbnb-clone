from typing import List

from .types import Form


def get_field_names_from_form(form: Form) -> List[str]:
    return list(form.base_fields.keys())
