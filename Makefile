VENV_NAME = .whisky_rec_venv
PYTHON = $(VENV_NAME)\Scripts\python

.PHONY: install
install:
	$(PYTHON) -m pip install --upgrade pip && $(PYTHON) -m pip install -r requirements.txt

.PHONY: test
test:
	$(PYTHON) -m pytest -vv tests/**/*.py

.PHONY: format
format:
	$(PYTHON) -m black scripts/**/*.py

.PHONY: lint
lint:
	$(PYTHON) -m pylint scripts/**/*.py

.PHONY: all
all: install lint test
