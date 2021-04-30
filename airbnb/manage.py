#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


django_settings_module: str = 'airbnb.settings.local'

if os.environ.get('ENVIRONMENT', 'local') == 'pro'.lower():
    django_settings_module = 'airbnb.settings.pro'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
