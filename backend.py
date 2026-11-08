import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "fleet.db"
DATA_DIR = Path(__file__).resolve().parent 

TABLE_FILES = {
    "vehicles": ("vehicles.csv", ["vehicle_id","registration_no","vehicle_type","model_year","status","odometer_km"]),
    "drivers": ("drivers.csv", ["driver_id","driver_name","phone","license_type","status"]),
    "fuel_records": ("fuel_records.csv", ["fuel_id","vehicle_id","date","litres","price_per_litre","total_cost","odometer_km"]),
    "maintenance_records": ("maintenance_records.csv", ["maintenance_id","vehicle_id","date","service_type","cost","status"]),
    "driver_schedules": ("driver_schedules.csv", ["schedule_id","driver_id","vehicle_id","date","start_location","destination","departure_time","status"]),
}

def connect():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY, registration_no TEXT UNIQUE,
            vehicle_type TEXT, model_year INTEGER, status TEXT, odometer_km INTEGER
        );
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id TEXT PRIMARY KEY, driver_name TEXT, phone TEXT,
            license_type TEXT, status TEXT
        );
        CREATE TABLE IF NOT EXISTS fuel_records (
            fuel_id TEXT PRIMARY KEY, vehicle_id TEXT, date TEXT, litres REAL,
            price_per_litre REAL, total_cost REAL, odometer_km INTEGER
        );
        CREATE TABLE IF NOT EXISTS maintenance_records (
            maintenance_id TEXT PRIMARY KEY, vehicle_id TEXT, date TEXT,
            service_type TEXT, cost REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS driver_schedules (
            schedule_id TEXT PRIMARY KEY, driver_id TEXT, vehicle_id TEXT,
            date TEXT, start_location TEXT, destination TEXT,
            departure_time TEXT, status TEXT
        );
        """)

        for table, (filename, columns) in TABLE_FILES.items():
            csv_path = DATA_DIR / filename

            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df = df[columns].drop_duplicates(
                    subset=[columns[0]]
                )

                placeholders = ",".join(["?"] * len(columns))
                column_names = ",".join(columns)

                query = (
                    f"INSERT OR IGNORE INTO {table} "
                    f"({column_names}) VALUES ({placeholders})"
                )

                con.executemany(
                    query,
                    df.astype(object).where(
                        pd.notna(df), None
                    ).values.tolist()
                )
def update_vehicle_status(vehicle_id, status):
    with connect() as con:
        con.execute(
            "UPDATE vehicles SET status=? WHERE vehicle_id=?",
            (status, vehicle_id)
        )
def get_table(table):
    if table not in TABLE_FILES:
        raise ValueError("Unknown table")

    with connect() as con:
        return pd.read_sql_query(
            f"SELECT * FROM {table}", con
        )
def add_record(table, values):
    if table not in TABLE_FILES:
        raise ValueError("Unknown table")

    columns = TABLE_FILES[table][1]

    placeholders = ",".join(["?"] * len(columns))
    column_names = ",".join(columns)

    query = (
        f"INSERT INTO {table} "
        f"({column_names}) VALUES ({placeholders})"
    )

    with connect() as con:
        con.execute(
            query,
            [values.get(col) for col in columns]
        )
def delete_record(table, id_column, record_id):
    if table not in TABLE_FILES:
        raise ValueError("Unknown table")

    if id_column != TABLE_FILES[table][1][0]:
        raise ValueError("Invalid ID column")

    with connect() as con:
        con.execute(
            f"DELETE FROM {table} WHERE {id_column} = ?",
            (record_id,)
        )
