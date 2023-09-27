install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

# lint:
# 	pylint --disable=R,C,pointless-statement,undefined-variable --extension-pkg-whitelist='pydantic' streamlit_app.py ./code_logic/*.py

# format:
# 	black streamlit_app.py ./code_logic/*.py

all: install lint format
