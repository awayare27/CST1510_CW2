from pathlib import Path

import pandas as pd
import requests

URL =  "https://earthquake.usgs.gov/fdsnws/event/1/query"
PARAMS= {"format": "geojson", "minmagnitude": 2.5, "limit": 500}
RECORDS_KEY="features"

RENAME = {"properties_mag": "mag", "properties_place": "place", "properties_time": "time",
          "properties_magType": "mag_type", "properties_sig": "significance", "properties_tsunami": "tsunami"}
KEEP = ["time", "place", "mag", "mag_type", "significance", "tsunami"]
MUST_HAVE = ["mag"] 

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


# ---- The functions ------------------------------------

def get_data(url, params):
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()          # turns 404, 500 ... into an error
        return response.json()
    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None
    
def make_table(data, records_key):
 records = data[RECORDS_KEY] if RECORDS_KEY else data
 table = pd.json_normalize(records, sep="_")
 return table

def tidy_data(df):
    tidy = df.rename(columns=RENAME)
    tidy = tidy[KEEP]
    tidy = tidy.dropna(subset=MUST_HAVE)
    print(tidy.shape)
    return tidy

def save_data(df, path):
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")

if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)
        print(table.head())
        save_data(table, RAW_FILE)

