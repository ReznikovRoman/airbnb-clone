include makefile.env
export

PIP_COMPILE_ARGS := --generate-hashes --no-header --verbose

.PHONY: compile-requirements
compile-requirements:
	pip-compile $(PIP_COMPILE_ARGS) requirements.in
	test -f requirements.local.in && pip-compile $(PIP_COMPILE_ARGS) requirements.local.in || exit 0

.PHONY: sync-requirements
sync-requirements:
	pip install pip-tools
	pip-sync requirements.txt requirements.*.txt

.PHONY: check
check:
	ec
	flake8
	isort -qc .

.PHONY: check-docker
check-docker:
	docker-compose -f $(DOCKER_COMPOSE_FILENAME) run --rm server sh -c "ec && flake8 && isort -qc ."

.DEFAULT_GOAL :=
