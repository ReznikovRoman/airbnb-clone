from accounts.forms import UserInfoForm
from common.services import get_field_names_from_form


def test_ok():
    """get_field_names_from_form() returns list of form fields."""
    result = get_field_names_from_form(form=UserInfoForm)

    assert result == ['first_name', 'last_name', 'email']
