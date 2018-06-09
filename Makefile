setup::
	@pipenv install --dev

lint::
	@pipenv run tidypy check

test::
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage report --rcfile=setup.cfg

ci:: test
	@pipenv run coveralls --rcfile=setup.cfg

clean::
	@rm -rf dist build .pytest_cache .coverage docs/build

build:: clean
	@pipenv run python setup.py sdist
	@pipenv run python setup.py bdist_wheel

docs::
	@rm -rf docs/build
	@cd docs && pipenv run make html

publish::
	@pipenv run twine upload dist/*

