from django.test import TestCase
from django.http import HttpResponse
from django.urls import reverse

from accounts.models import CustomUser
from hosts.models import RealtyHost


class BecomeHostViewTests(TestCase):
    def setUp(self):
        # create 3 users
        test_user1 = CustomUser.objects.create_user(
            email='test1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='123',
        )
        test_user2 = CustomUser.objects.create_user(
            email='test2@gmail.com',
            first_name='Bill',
            last_name='Smith',
            password='123',
        )
        test_user3 = CustomUser.objects.create_user(
            email='test3@gmail.com',
            first_name='David',
            last_name='Brown',
            password='123',
        )

        # confirm an email for 2 users
        test_user1.is_email_confirmed = True
        test_user2.is_email_confirmed = True

        # add profile image for 1 user
        test_user1.profile.profile_image = 'image.png'
        test_user1.profile.save()

        test_user1.save()
        test_user2.save()
        test_user3.save()

        # create 1 host
        test_host1 = RealtyHost.objects.create(
            user=test_user1,
        )
        test_host1.save()

    def test_redirect_if_not_logged_in(self):
        response: HttpResponse = self.client.get('/hosts/become-a-host/')
        self.assertRedirects(response, '/accounts/login/?next=/hosts/become-a-host/')

    def test_redirect_if_not_email_confirmed(self):
        login = self.client.login(username='test3@gmail.com', password='123')
        response = self.client.get('/hosts/become-a-host/')

        # check that user is logged in
        self.assertEqual(str(response.context['user']), 'test3@gmail.com')

        # check if there was a redirect
        self.assertRedirects(response, '/accounts/activation-required/')

    def test_redirect_if_no_profile_image(self):
        login = self.client.login(username='test2@gmail.com', password='123')
        response = self.client.get('/hosts/become-a-host/')

        self.assertRedirects(response, '/hosts/become-a-host/missing-image/')

    def test_desired_redirect_if_required_data_exists(self):
        login = self.client.login(username='test1@gmail.com', password='123')
        response = self.client.get('/hosts/become-a-host/', follow=True)

        self.assertRedirects(response, '/realty/new/info/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='test1@gmail.com', password='123')
        response = self.client.get(reverse('hosts:become_a_host'), follow=True)

        self.assertRedirects(response, '/realty/new/info/')
