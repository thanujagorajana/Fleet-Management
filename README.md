# Fleet Management System

A beginner-friendly Python + Streamlit fleet management dashboard.

## Features
- Dashboard summary and charts
- Vehicle records (add, update status, delete)
- Driver records (add and view)
- Fuel tracking
- Maintenance records
- Driver scheduling
- CSV reports/downloads

## Project files
- `dashboard.py`: Streamlit user interface
- `backend.py`: SQLite database operations and CSV import
- `fleet.db`: created automatically the first time the app runs
- `data/`: sample CSV datasets
- `requirements.txt`: Python packages

## Run on Windows
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Install packages: `python -m pip install -r requirements.txt`
4. Start dashboard: `python -m streamlit run dashboard.py`
5. Open the Local URL shown in Command Prompt, usually http://localhost:8501

The sample CSV data is imported into `fleet.db` automatically when the database tables are empty.
Use sample data only; do not upload private company or personal information.


## Sample dataset size
The included expanded sample data contains:
- 40 vehicle records
- 30 driver records
- 180 fuel records
- 100 maintenance records
- 120 driver schedule records

All records are synthetic demonstration data, not real fleet or personal records.
