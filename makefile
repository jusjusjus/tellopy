
test:
	mypy --ignore-missing-imports tellopy
	pytest --cov

install:
	pip install -r requirements.txt
	conda install -c conda-forge av
