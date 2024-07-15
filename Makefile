VENV_NAME = .whisky_rec_venv
PYTHON = $(VENV_NAME)\Scripts\python

# Define variables for Docker and Lambda layer
LAMBDA_DOCKER_IMAGE_NAME = chromium-layer
LAMBDA_LAYER_DIR = lambda_layer
LAMBDA_LAYER_ZIP = chromium_layer.zip

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
	# Navigate to the lambda_layer directory and build the Docker image
	cd $(LAMBDA_LAYER_DIR) && docker build -t $(LAMBDA_DOCKER_IMAGE_NAME) .

	# Run the Docker container to create the layer zip file
	cd $(LAMBDA_LAYER_DIR) && docker run --rm -v $(CURDIR):/mnt/data $(LAMBDA_DOCKER_IMAGE_NAME)

	# Output message
	@echo "Lambda layer zip file created at $(LAMBDA_LAYER_DIR)/$(LAMBDA_LAYER_ZIP)"

.PHONY: clean_layer
clean_layer:
	del $(LAMBDA_LAYER_DIR)\$(LAMBDA_LAYER_ZIP)

.PHONY: all
all: install lint test

# Including build_layer as part of the full workflow
.PHONY: full
full: all build_layer
