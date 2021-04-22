from typing import List

from .collections import FormWithModel
from .types import AbstractForm


def get_field_names_from_form(form: AbstractForm) -> List[str]:
    return list(form.base_fields.keys())


def create_name_with_prefix(name: str, prefix: str) -> str:
    prefix = f"{prefix}_" if not prefix.endswith('_') else prefix
    return f"{prefix}{name}" if not name.startswith(prefix) else name


def get_required_fields_from_form_with_model(forms_with_models: List[FormWithModel]) -> List[str]:
    """Return all required fields (fields that cannot be blank) from form and linked model."""
    required_fields: List[str] = []
    for form_with_model in forms_with_models:
        required_fields.extend([field for field in form_with_model.form.base_fields
                                if not form_with_model.model._meta.get_field(field).blank])
    return required_fields


def set_prefixes_for_names(names: List[str], prefix: str = '') -> List[str]:
    return [create_name_with_prefix(name, prefix) for name in names]
