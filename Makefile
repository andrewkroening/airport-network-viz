install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,pointless-statement,undefined-variable --extension-pkg-whitelist='pydantic' streamlit_app.py

format:
	black streamlit_app.py

all: install lint format
