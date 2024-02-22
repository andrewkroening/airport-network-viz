install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,pointless-statement,undefined-variable,unused-variable,unused-import,no-member --extension-pkg-whitelist='pydantic' *.py

format:
	black *.py

all: install lint format
