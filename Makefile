web:
	sphinx-build webpage/source webpage/build

full-pipeline:
	python3 tips/download_data.py
	python3 main.py
	sphinx-build webpage/source webpage/build