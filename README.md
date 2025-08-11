# clone (after I push to GitHub or I give you zip)
git clone <repo_url>
cd vehicle-dashboard

# create venv
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# create DB from schema
sqlite3 data/vahan.db < src/db/schema.sql

# run tests
python -m pytest

# run Streamlit app
streamlit run src/dashboard/app.py
