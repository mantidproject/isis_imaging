AUTHENTICATION_PARAMS=--user $$UPLOAD_USER --token $$ANACONDA_API_TOKEN

#Needed because each command is run in a new shell
SHELL=/bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

install-conda-env:
	conda env create -f environment.yml

install-run-requirements:
	conda install --yes --only-deps -c $$UPLOAD_USER mantidimaging

install-build-requirements:
	@echo "Installing packages required for starting the build process"
	conda create -n build-env
	$(CONDA_ACTIVATE) build-env ; conda install --yes conda-build anaconda-client conda-verify

install-dev-requirements:
	conda env create -f environment-dev.yml

build-conda-package: .remind-current install-build-requirements
	# intended for local usage, does not install build requirements
	$(CONDA_ACTIVATE) build-env ; conda-build ./conda --label unstable

build-conda-package-nightly: .remind-current .remind-for-user .remind-for-anaconda-api install-build-requirements
	$(CONDA_ACTIVATE) build-env ; conda-build ./conda $(AUTHENTICATION_PARAMS) --label nightly

build-conda-package-release: .remind-current .remind-for-user .remind-for-anaconda-api install-build-requirements
	$(CONDA_ACTIVATE) build-env ; conda-build ./conda $(AUTHENTICATION_PARAMS)

.remind-current:
	@echo "Make sure the correct channels are added in \`conda config --get channels\`"
	@echo "Currently the required channels are \`conda-forge\` and \`defaults\`"
	@echo "Current: $$(conda config --get channels)"
	@echo "If automatic upload is wanted, then \`conda config --set anaconda_upload yes\` should be set."
	@echo "Current: $$(conda config --get anaconda_upload)"

.remind-for-user:
	@if [ -z "$$UPLOAD_USER" ]; then echo "Environment variable UPLOAD_USER not set!"; exit 1; fi;

.remind-for-anaconda-api:
	@if [ -z "$$ANACONDA_API_TOKEN" ]; then echo "Environment variable ANACONDA_API_TOKEN not set!"; exit 1; fi;


test-env:
	conda env create -n test-env -f environment-dev.yml

test:
	python -m pytest

mypy:
	python -m mypy --ignore-missing-imports --no-site-packages mantidimaging

yapf:
	python -m yapf --parallel --diff --recursive .

yapf_apply:
	python -m yapf -i --parallel --recursive .

flake8:
	python -m flake8

check: yapf flake8 mypy test
