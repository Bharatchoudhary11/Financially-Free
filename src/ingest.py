# src/ingest.py
import sqlite3
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

DB_PATH = "data/vahan.db"
URL = "https://vahan.parivahan.gov.in/vahan4dashboard/"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            category TEXT,
            manufacturer TEXT,
            month TEXT,
            registrations INTEGER
        )
    """)
    conn.close()
    print("Ensured 'registrations' table exists.")

def fetch_vahan_data():
    options = Options()
    options.add_argument("--headless")  # Run without opening a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(6)  # wait for JS to load tables

    # Scrape all HTML tables from the page
    tables = pd.read_html(driver.page_source)
    driver.quit()

    # You may need to inspect which table index contains the correct data
    # For example: table 0 might be summary, table 1 might be manufacturer data
    df = tables[0]  # Change if your target is another table index
    print(f"Fetched {len(df)} rows from Vahan Dashboard.")
    return df

def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("registrations", conn, if_exists="replace", index=False)
    conn.close()
    print("Data saved to database.")

if __name__ == "__main__":
    init_db()
    df = fetch_vahan_data()
    save_to_db(df)
