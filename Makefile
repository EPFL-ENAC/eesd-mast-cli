url=http://localhost:8000

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

rm-all:
	for i in `seq 1 48` ; do \
		poetry run mast rm-reference $$i --recursive --force --url $(url) --key $(key) ; \
	done

upload-all:
	poetry run mast upload $(file) --url $(url) --key $(key)