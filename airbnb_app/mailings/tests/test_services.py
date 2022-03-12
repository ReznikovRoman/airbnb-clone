from django.core import mail
from django.test import TestCase

from ..services import send_email_to_user, send_email_with_attachments


class MailingsServicesTests(TestCase):
    def test_send_email_to_user_valid_content(self):
        """send_email_to_user() creates and sends an email with the given parameters (subject, body, etc.)."""
        send_email_to_user(
            subject='Test',
            message='Test message',
            email_to=['test@gmail.com'],
            email_from='admin@gmail.com',
        )
        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.subject, 'Test')
        self.assertEqual(test_email.body, 'Test message')
        self.assertEqual(test_email.to, ['test@gmail.com'])
        self.assertEqual(test_email.from_email, 'admin@gmail.com')

    def test_send_email_with_attachments_valid_content(self):
        """send_email_with_attachments() creates and sends an email with optional alternatives (html, plain text)."""
        test_html_content = """<p>Test html</p>"""
        send_email_with_attachments(
            subject='Test',
            body='Test body',
            email_to=['test@gmail.com'],
            email_from='admin@gmail.com',
            alternatives=[
                (test_html_content, 'text/html'),
            ],
        )
        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.subject, 'Test')
        self.assertEqual(test_email.body, 'Test body')
        self.assertEqual(test_email.to, ['test@gmail.com'])
        self.assertEqual(test_email.from_email, 'admin@gmail.com')

        self.assertEqual(len(test_email.alternatives), 1)
        self.assertEqual(test_email.alternatives[0][0], test_html_content)
