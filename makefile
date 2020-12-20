.PHONY: lint lint.fix static_analysis test install install.dev init.conda

lint:
	flake8 tellopy

lint.fix:
	autopep8 -r -i tellopy/

static_analysis:
	mypy --ignore-missing-imports tellopy

test:
	pytest -x

init.conda:
	conda create -y -n tello python=3.6
	conda activate tello

install:
	conda install -y -c anaconda pyaudio
	pip install -r requirements.txt
	conda install -y -c conda-forge av

install.dev:
	pip install -r requirements-dev.txt
