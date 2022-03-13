include makefile.env

REQUIREMENTS_DIR := requirements
PIP_COMPILE_ARGS := --generate-hashes --no-header --no-emit-index-url --verbose
PIP_COMPILE := cd $(REQUIREMENTS_DIR) && pip-compile $(PIP_COMPILE_ARGS)

.PHONY: fix
fix:
	isort .

.PHONY: lint
lint:
	ec
	flake8
	isort -qc .

.PHONY: test
test:
	cd /app/airbnb_app && pytest -n 4 --ff -x --cov-report=xml --cov=. -m 'not single_thread'
	cd /app/airbnb_app && pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	cd /app/airbnb_app && pytest --dead-fixtures

.PHONY: check
check: lint test

.PHONY: dc
dc:
	docker-compose -f $(DOCKER_COMPOSE_FILENAME) run --rm server bash -c "make check"

.PHONY: compile-requirements
compile-requirements:
	pip install -U pip-tools
	$(PIP_COMPILE) requirements.in
	$(PIP_COMPILE) requirements.linter.in
	$(PIP_COMPILE) requirements.test.in
	test -f $(REQUIREMENTS_DIR)/requirements.local.in && $(PIP_COMPILE) requirements.local.in || exit 0

.PHONY: sync-requirements
sync-requirements:
	pip install -U pip-tools
	cd $(REQUIREMENTS_DIR) && pip-sync requirements.txt requirements.*.txt

.DEFAULT_GOAL :=
