import shutil
import tempfile

from django.test import TestCase, override_settings

from accounts.models import CustomUser
from addresses.models import Address
from common.testing_utils import create_valid_image
from hosts.models import RealtyHost

from ..models import Realty, RealtyImage, RealtyTypeChoices


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class OrderFieldTests(TestCase):
    def setUp(self) -> None:
        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        test_host1 = RealtyHost.objects.create(user=test_user1)
        test_location1 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Arbat, 20',
        )
        self.test_realty1 = Realty.objects.create(
            name='Realty 1',
            description='Desc 1',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location1,
            host=test_host1,
        )

        test_image_name1 = 'image1.png'
        test_image1 = create_valid_image(test_image_name1)

        RealtyImage.objects.create(
            image=test_image1,
            realty=self.test_realty1,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        super().tearDownClass()

    def test_initial_order_is_zero(self):
        """Test that if there are no items related to the model, initial order is 0."""
        realty_image: RealtyImage = RealtyImage.objects.first()
        self.assertEqual(realty_image.order, 0)

    def test_correct_order_if_multiple_items(self):
        """Test that each new item with the `order` field has a correct order."""
        realty_image1: RealtyImage = RealtyImage.objects.first()

        # create new image
        test_image_name2 = 'image2.png'
        test_image2 = create_valid_image(test_image_name2)
        realty_image2: RealtyImage = RealtyImage.objects.create(image=test_image2, realty=self.test_realty1)

        realty_image1.refresh_from_db()
        realty_image2.refresh_from_db()

        # ordering is correct
        self.assertEqual(realty_image1.order, 0)
        self.assertEqual(realty_image2.order, 1)

    def test_correct_order_if_value_passed_manually(self):
        """Test that `order` value can be passed manually."""
        realty_image1: RealtyImage = RealtyImage.objects.first()

        # create new image
        test_image_name2 = 'image2.png'
        test_image2 = create_valid_image(test_image_name2)
        # pass `order` value as an argument
        realty_image2: RealtyImage = RealtyImage.objects.create(image=test_image2, realty=self.test_realty1, order=2)

        realty_image1.refresh_from_db()
        realty_image2.refresh_from_db()

        # ordering is correct
        self.assertEqual(realty_image1.order, 0)
        self.assertEqual(realty_image2.order, 2)
