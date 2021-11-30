# Django guides


## App structure

Example for app with html templates:
```
app
|   __init__.py
|   admin.py
|   apps.py
|   forms.py
|   models.py
|   services.py
|   tasks.py
|   urls.py
|   views.py
|
└───templates
│   │
│   └─────app
│         │
│         └───profiles
│             │   list.html
│             │   detail.html
│
└───tests
│   │   test_services.py
│   │   test_views.py
│
└───migrations
│   │   __init__.py
│   │   0001_initial.py
│   │   0002_fill_countries.py
```

Example for app with DRF:
URL routes are stored in `api.v1.<app_name>.urls`
```
api
│   __init__.py
│   permissions.py
│   ...
│
└───v1
│   │   __init__.py
│   │   urls.py
│   │
│   └───app
│       │   __init__.py
│       │   urls.py
```
```
app
|   __init__.py
|   admin.py
|   apps.py
|   serializers.py
|   models.py
|   services.py
|   tasks.py
|   views.py
│
└───tests
│   │   test_services.py
│   │   test_views.py
│
└───migrations
│   │   __init__.py
│   │   0001_initial.py
│   │   0002_fill_countries.py
```

## Cookie Cutter
It is recommended to start project with some kind of cookiecutter.
Having the proper structure from the start pays off.

Example:
- [django-drf cookiecutter](https://github.com/ReznikovRoman/cookiecutter-django-drf)

## Models
Models should take care of the data model and not much else.

Do not put any business logic in model methods (there are only a few exceptions).

### Fields validation

The Django's documentation on constraints is quite lean,
so you can check the following articles by Adam Johnson, for examples of how to use them:

1. [Using Django Check Constraints to Ensure Only One Field Is Set](https://adamj.eu/tech/2020/03/25/django-check-constraints-one-field-set/)
2. [Django’s Field Choices Don’t Constrain Your Data](https://adamj.eu/tech/2020/01/22/djangos-field-choices-dont-constrain-your-data/)
3. [Using Django Check Constraints to Prevent Self-Following](https://adamj.eu/tech/2021/02/26/django-check-constraints-prevent-self-following/)

## Business logic
- Store business logic in `services.py` file or in a `service/` package.
- A service can be:
  - A simple function
  - A class
  - An entire module
- Methods and functions from `services.py` files are called only with positional arguments.
- Service functions take keyword-only arguments
- Services are type-annotated
- A service does business logic - from simple model creation to complex cross-cutting concerns, to calling external services & tasks
