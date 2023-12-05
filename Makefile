data="../backend/scripts/Shake_Table_Tests_Database_v01.xlsx"

install:
	poetry install

test:
	poetry run pytest

build:
	poetry build

clean:
	rm -rf dist

local-install:
	pip install ./dist/*.tar.gz 