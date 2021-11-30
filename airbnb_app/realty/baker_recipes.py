from model_bakery import seq
from model_bakery.recipe import Recipe, foreign_key

from addresses.baker_recipes import address
from hosts.baker_recipes import host

from .models import Realty


available_realty = Recipe(
    _model=Realty,
    location=foreign_key(address, one_to_one=True),
    host=foreign_key(host),
    name=seq("Test Realty - "),
    description=seq("Test description for realty -"),
    is_available=True,
)

unavailable_realty = available_realty.extend(
    is_available=False,
)
