VENV_NAME = .whisky_rec_venv
PYTHON = $(VENV_NAME)\Scripts\python

.PHONY: install
install:
	$(PYTHON) -m pip install --upgrade pip && pip install -r requirements.txt

.PHONY: test
test:
	$(PYTHON) -m pytest -vv tests/test_data_parsing.py

.PHONY: format
format:
	$(PYTHON) -m black tests/test_data_parsing.py

.PHONY: lint
lint:
	$(PYTHON) -m pylint tests/test_data_parsing.py

.PHONY: all
all: install lint test
