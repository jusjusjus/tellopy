.PHONY: start.manual start.manual.mockup \
	    check.lint check.lint.fix check.types check.units check.integration \
	    install install.dev init.conda

start.manual:
	python -m tellopy.manual

start.manual.mockup:
	python -m tellopy.manual --mockup

check.lint:
	flake8 tellopy/ tests/

check.lint.fix:
	autopep8 -r -i tellopy/ tests/

check.types:
	mypy --ignore-missing-imports tellopy/ tests/

check.integration:
	python -m pytest -x tests/integration

check.units:
	python -m pytest -x tests/unit

init.conda:
	conda create -y -n tello python=3.6

install:
	conda install -y -c anaconda pyaudio
	pip install -r requirements.txt
	conda install -y -c conda-forge av

install.dev:
	pip install -r requirements-dev.txt
