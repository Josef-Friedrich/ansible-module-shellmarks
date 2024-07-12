test:
	poetry run tox

install: update

# https://github.com/python-poetry/poetry/issues/34#issuecomment-1054626460
install_editable:
	pip install -e .

install_library:
	cp shellmarks.py /etc/ansible/library/shellmarks.py

debug: install_library
	ansible -m shellmarks -a "export='zoxide add %path'" localhost -v

update:
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

format:
	poetry run tox -e format

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html > /dev/null 2>&1

lint:
	poetry run tox -e lint

.PHONY: test install install_editable install_library update build publish format docs lint pin_docs_requirements
