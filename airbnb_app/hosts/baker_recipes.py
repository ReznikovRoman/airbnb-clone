from itertools import cycle

from model_bakery.recipe import Recipe, foreign_key, seq

from accounts.models import CustomUser, ProfileGenderChoices

from .models import RealtyHost


host_ratings = [1, 2, 3, 4, 5]
host_profile_gender_choices = [
    ProfileGenderChoices.MALE,
    ProfileGenderChoices.FEMALE,
    ProfileGenderChoices.OTHER,
]

host_user = Recipe(
    _model=CustomUser,
    email=seq('host', suffix='@airproject.host.com'),
    first_name=seq('Host-'),
    last_name=seq('Smith-'),
    is_email_confirmed=True,
)

host = Recipe(
    _model=RealtyHost,
    user=foreign_key(host_user, one_to_one=True),
    host_rating=cycle(host_ratings),
)
