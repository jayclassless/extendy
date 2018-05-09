setup::
	@pipenv install --dev

lint::
	@pipenv run tidypy check

test::
	@pipenv run pip install --editable test/testpkg
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage report --rcfile=setup.cfg

ci:: test
	@pipenv run coveralls --rcfile=setup.cfg

clean::
	@rm -rf dist build .pytest_cache .coverage

build:: clean
	@python setup.py sdist
	@python setup.py bdist_wheel

publish::
	@twine upload dist/*

