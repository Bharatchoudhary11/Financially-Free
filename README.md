# clone (after I push to GitHub or I give you zip)
git clone <repo_url>
cd vehicle-dashboard

# create venv
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# populate the SQLite database (reads data/vahan.csv if available)
# place the Vahan Excel export at ``data/vahan.csv`` or the script will
# fall back to sample data
python src/ingest.py

# run tests
python -m pytest

# run Streamlit app
streamlit run src/dashboard/app.py
