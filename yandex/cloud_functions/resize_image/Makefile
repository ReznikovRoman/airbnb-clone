PIP_COMPILE_ARGS := --generate-hashes --no-header --verbose

.PHONY: compile-requirements
compile-requirements:
	pip install -U pip-tools
	pip-compile $(PIP_COMPILE_ARGS) requirements.in
	pip-compile $(PIP_COMPILE_ARGS) requirements.dev.in

.PHONY: sync-requirements
sync-requirements:
	pip install -U pip-tools
	pip-sync requirements.txt requirements.*.txt

.PHONY: check
check:
	ec
	flake8
	isort -qc .

.DEFAULT_GOAL :=
