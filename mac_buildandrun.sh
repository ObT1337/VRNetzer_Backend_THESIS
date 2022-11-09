#!bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r extensions/StringEx/requirements.txt
python -m pip install -r extensions/StringEx/cartographs_requirements.txt
python -m pip install -r requirements.txt
flask run --host=0.0.0.0 --port 3000

