VENV_NAME = .whisky_rec_venv
PYTHON = $(VENV_NAME)\Scripts\python

# Define variables for Docker and Lambda layer
DOCKER_IMAGE_NAME = chromium-layer
LAYER_DIR = lambda_layer
LAYER_ZIP = chromium_layer.zip

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

.PHONY: build_layer
build_layer:
	cd $(LAYER_DIR) && docker build -t $(DOCKER_IMAGE_NAME) . && \
	docker run --rm -v "%cd%:/mnt/data" $(DOCKER_IMAGE_NAME)
	@echo "Lambda layer zip file created at $(LAYER_DIR)/$(LAYER_ZIP)"

.PHONY: clean_layer
clean_layer:
	del $(LAYER_DIR)\$(LAYER_ZIP)

.PHONY: all
all: install lint test

# Including build_layer as part of the full workflow
.PHONY: full
full: all build_layer
