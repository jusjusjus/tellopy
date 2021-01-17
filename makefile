.PHONY: lint lint.fix static_analysis test install install.dev init.conda

check.linting:
	flake8 tellopy

check.linting.fix:
	autopep8 -r -i tellopy/

check.types:
	mypy --ignore-missing-imports tellopy

check.integration:
	python -m pytest -x tests/integration

check.units:
	python -m pytest -x tests/unit

test:
	pytest -x

init.conda:
	conda create -y -n tello python=3.6

install:
	conda install -y -c anaconda pyaudio
	pip install -r requirements.txt
	conda install -y -c conda-forge av

install.dev:
	pip install -r requirements-dev.txt
