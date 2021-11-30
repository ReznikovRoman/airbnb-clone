from random import choice, randint, sample
from typing import List

from model_bakery import baker

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile, ProfileGenderChoices
from hosts.models import RealtyHost
from realty.models import Amenity, RealtyTypeChoices


class Command(BaseCommand):
    help = "Populates database with initial data."

    def handle(self, *args, **options):
        # create users
        self._create_users(quantity=10)

        # create hosts
        self._create_hosts(5)
        realty_hosts = RealtyHost.objects.filter(
            user__email__startswith="host",
            user__email__endswith="@airproject.host.com",
        )

        # create amenities
        self._create_amenities()
        amenities = list(Amenity.objects.all())

        # create realty
        realty_amenities_quantity = 3
        realty_type_choices = [
            RealtyTypeChoices.APARTMENTS,
            RealtyTypeChoices.HOTEL,
            RealtyTypeChoices.HOUSE,
        ]
        for realty_host in realty_hosts:
            realty_available_quantity = randint(1, 5)
            realty_unavailable_quantity = randint(0, 2)
            self._update_realty_host_profile(profile=realty_host.user.profile)

            self.stdout.write(
                msg=self.style.WARNING(f"Creating <{realty_available_quantity}> new fake available realty..."),
            )
            for available_realty in range(realty_available_quantity):
                baker.make_recipe(
                    baker_recipe_name="realty.available_realty",
                    host=realty_host,
                    amenities=sample(amenities, realty_amenities_quantity),
                    beds_count=randint(1, 8),
                    max_guests_count=randint(1, 100),
                    price_per_night=randint(1, 32_767),
                    realty_type=choice(realty_type_choices),
                )

            self.stdout.write(
                msg=self.style.WARNING(f"Creating <{realty_unavailable_quantity}> new fake unavailable realty..."),
            )
            for unavailable_realty in range(realty_unavailable_quantity):
                baker.make_recipe(
                    baker_recipe_name="realty.unavailable_realty",
                    host=realty_host,
                    amenities=sample(amenities, realty_amenities_quantity),
                    beds_count=randint(1, 8),
                    max_guests_count=randint(1, 100),
                    price_per_night=randint(1, 32_767),
                    realty_type=choice(realty_type_choices),
                )

    def _create_users(self, quantity: int) -> None:
        self.stdout.write(self.style.WARNING(f"Creating {quantity}> new fake users..."))
        baker.make_recipe("accounts.confirmed_email_user", _quantity=quantity)
        baker.make_recipe("accounts.unconfirmed_email_user", _quantity=quantity)

    def _create_hosts(self, quantity: int) -> List[RealtyHost]:
        self.stdout.write(self.style.WARNING(f"Creating <{quantity}> new fake hosts..."))
        return baker.make_recipe("hosts.host", _quantity=quantity)

    def _create_amenities(self) -> None:
        self.stdout.write(self.style.WARNING("Creating new fake amenities..."))
        amenity_names = [
            "Wi-Fi",
            "Free parking",
            "Pool",
            "Jacuzzi",
            "Kitchen",
            "Air conditioning",
            "Heating",
            "Washer",
            "TV or cable",
        ]
        for amenity_name in amenity_names:
            Amenity.objects.get_or_create(name=amenity_name)

    def _update_realty_host_profile(self, profile: Profile):
        host_profile_gender_choices = [
            ProfileGenderChoices.MALE,
            ProfileGenderChoices.FEMALE,
            ProfileGenderChoices.OTHER,
        ]
        profile.gender = choice(host_profile_gender_choices)
        profile.phone_number = self._gen_phone()
        profile.is_phone_number_confirmed = True
        profile.date_of_birth = timezone.now().date()
        profile.save(
            update_fields=[
                "phone_number",
                "is_phone_number_confirmed",
                "date_of_birth",
                "gender",
            ],
        )

    @staticmethod
    def _gen_phone():
        first = str(randint(100, 999))
        second = str(randint(1, 888)).zfill(3)

        last = (str(randint(1, 9998)).zfill(4))
        while last in ['1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888']:
            last = (str(randint(1, 9998)).zfill(4))

        return f"+7{first}{second}{last}"
