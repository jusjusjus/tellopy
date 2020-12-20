
test:
	mypy --ignore-missing-imports tellopy
	pytest

install:
	conda install -y -c anaconda pyaudio
	pip install -r requirements.txt
	conda install -y -c conda-forge av
