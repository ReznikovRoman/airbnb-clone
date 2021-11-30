# Python guides

## Overview

- Python 3.9
- PEP8
- TDD

## Comments

- Docstrings for models, forms, views, etc. are preferred (but not required).
- Docstrings for unit tests are required.

### Docstrings

One-line docstring:
```python
"""Sends an email to all active subscribers."""
```

Multiline docstring:
```python
"""Starts the task chain.

1. Fetches data from external API.
2. Sends a verification email.
3. ...
"""
```

### Inline comments

Do not use inline comments to divide code into sections.
Instead, you'd better refactor this part and split it into smaller methods.

Inline comment:
```python
# calculate total price based on purchase history (refer to #174 for formula explanation)
```

## Imports

[isort](https://github.com/PyCQA/isort) is configured to sort imports.

imports order:
1. `__future__`
2. python standard library
3. third party
4. django
5. first party (local applications)
6. local folder
7. imports for type hints

Example:
```python
from __future__ import annotations

from typing import TYPE_CHECKING, Type

from celery import chain

from django.db.models import F

from accounts.services import send_greeting_email

from .tasks import send_email_to_user

if TYPE_CHECKING:
    from subscribers.models import Subscriber
```

## Long lines wrapping

Examples:
```python
if (
    condition_1 and
    condition_2 and
    not condition_3
):
    ...
```
```python
search_vector = (
    SearchVector('name', weight='A') +
    SearchVector('location__city', weight='B') +
    SearchVector('description', weight='B')
)
```
```python
long_text = (
    "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium, "
    "asperiores consequatur dolor ea enim esse explicabo ipsa, magni minus, "
    "praesentium recusandae reiciendis sint temporibus! Accusantium ad aliquid blanditiis commodi culpa, "
    "earum error excepturi explicabo harum iusto molestias mollitia porro quidem quis repudiandae "
    "sapiente suscipit tempore ullam, unde vel velit voluptatum!"
)
```
```python
User.objects.filter(
    email__startswith="temp.",
    email__icontains="@project.test.com",
).delete()
```
```python
courses = (
    Course.objects.
    filter(
        id__in=[course_recommendations],
        start_at__range=course_recommendation_date_range,
    )
    .exclude(cover_image='')
    .order_by('-created_at')
)
```

## Function calls and arguments

When calling a function, specify argument names if they are unclear from the name of the function alone.
You may write them even if they are obvious.

Example:
```python
from django.core.mail import EmailMultiAlternatives


email = EmailMultiAlternatives(
    subject=subject,
    body=body,
    from_email=email_from,
    to=email_to,
)
```
