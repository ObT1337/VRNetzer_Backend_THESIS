#!bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r extensions/StringEx/requirements.txt | grep -v 'already satisfied'
python -m pip install -r extensions/StringEx/cartographs_requirements.txt | grep -v 'already satisfied'
python -m pip install cartoGRAPHs | grep -v 'already satisfied'
python -m pip install -r extensions/ProteinStructureFetch/requirements.txt | grep -v 'already satisfied'
# python -m pip install -i https://test.pypi.org/simple/ vrprot
python -m pip install -r requirements.txt | grep -v 'already satisfied'
export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_RELOAD=1
flask run --with-threads --reload --host=0.0.0.0 --port 3000

