develop:
	vstrap init

# Run all tests
test:
	nosetests -d
	python tests/large/runner.py

# Run medium and small tests only
medium-test:
	nosetests -a '!large' -d

# Run small tests only
small-test:
	nosetests -A 'not (medium or large)' -d
