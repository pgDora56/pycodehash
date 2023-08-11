none:
	@echo "Required argument"

compile:
	python3 setup.py sdist bdist_wheel

upload:
	twine upload --repository pypi dist/*

test:
	python3 -m unittest discover tests

clear:
	rm -Rf naist_codehash.egg-info dist