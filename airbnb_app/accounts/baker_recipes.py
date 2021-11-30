from model_bakery.recipe import Recipe, seq

from .models import CustomUser


confirmed_email_user = Recipe(
    _model=CustomUser,
    email=seq('user', suffix='@airproject.user.com'),
    first_name=seq('John-'),
    last_name=seq('Doe-'),
    is_email_confirmed=True,
)

unconfirmed_email_user = confirmed_email_user.extend(
    first_name=seq('Bill-'),
    last_name=seq('Collins-'),
    is_email_confirmed=False,
)
