
test:
	mypy --ignore-missing-imports tellopy
	pytest

install:
	pip install -r requirements.txt
	conda install -c conda-forge av
