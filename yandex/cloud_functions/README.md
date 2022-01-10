# Yandex Cloud Functions

## Overview
Docs: https://cloud.yandex.com/en-ru/docs/functions/quickstart/

Folder structure:
```
function_name
|   build.zip
|   deploy.sh
|   Makefile
|   requirements.in
|   requirements.txt
|   setup.cfg
│
└───src
│   │   .env
│   │   __init__.py
│   │   build.py
│   │   example.env
│   │   main.py
```

- `build.zip` - function source package
- `deploy.sh` - deployment script. [Yandex.Cloud CLI](https://cloud.yandex.com/en-ru/docs/cli/quickstart) must be configured
- `main.py` has a `handler(event, context)` function - [request handler](https://cloud.yandex.com/en-ru/docs/functions/lang/python/handler)
