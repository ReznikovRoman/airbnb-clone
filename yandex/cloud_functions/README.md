# Yandex Cloud Functions

## Overview
Docs: https://cloud.yandex.com/en-ru/docs/functions/quickstart/

Structure:
```
function_name
|   .env
│   build.py
|   build.zip
|   deploy.sh
│   example.env
|   Makefile
|   requirements.in
|   requirements.txt
|   setup.cfg
│
└───src
│   │   __init__.py
│   │   main.py
```

- `build.zip` - function source package
- `deploy.sh` - deployment script. [Yandex.Cloud CLI](https://cloud.yandex.com/en-ru/docs/cli/quickstart) must be configured
- `main.py` has a `handler(event, context)` function - [request handler](https://cloud.yandex.com/en-ru/docs/functions/lang/python/handler)
