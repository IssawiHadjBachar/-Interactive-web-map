from flask import Flask, render_template, jsonify
import os
import pandas as pd
from collections import defaultdict
from itertools import groupby

app = Flask(__name__)
DATA_DIR = "data"
cached_data = None  # Cache for preprocessed station data

def extract_first_number(value):
    try:
        num = str(value).split(',')[0]
        return float(num) / 10 if num not in ['9999', '99999'] else None
    except:
        return None

def group_years(years):
    years = sorted(int(y) for y in years)
    ranges = []
    for _, g in groupby(enumerate(years), lambda ix: ix[0] - ix[1]):
        group = list(g)
        start, end = group[0][1], group[-1][1]
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
    return ranges

def load_station_data():
    global cached_data
    if cached_data is not None:
        return cached_data

    variable_years = defaultdict(set)
    station_info = {}

    for year in os.listdir(DATA_DIR):
        year_path = os.path.join(DATA_DIR, year)
        if not os.path.isdir(year_path):
            continue

        for file in os.listdir(year_path):
            if not file.endswith('.csv'):
                continue
            file_path = os.path.join(year_path, file)

            try:
                df = pd.read_csv(file_path, low_memory=False)

                if 'LATITUDE' not in df.columns or 'LONGITUDE' not in df.columns:
                    print(f"⚠️ Skipping {file_path}: missing LATITUDE or LONGITUDE columns.")
                    continue
                if df['LATITUDE'].dropna().empty or df['LONGITUDE'].dropna().empty:
                    print(f"⚠️ Skipping {file_path}: LATITUDE or LONGITUDE data is empty.")
                    continue

                lat = df['LATITUDE'].dropna().iloc[0]
                lon = df['LONGITUDE'].dropna().iloc[0]
                if pd.isna(lat) or pd.isna(lon):
                    print(f"⚠️ Skipping {file_path}: LAT/LON is NaN.")
                    continue

                station_id = file.split('.')[0]
                name = df['NAME'].iloc[0] if 'NAME' in df.columns else 'Unknown'
                elevation = df['ELEVATION'].iloc[0] if 'ELEVATION' in df.columns else 'Unknown'

                station_info[(lat, lon)] = {
                    'latitude': lat,
                    'longitude': lon,
                    'id': station_id,
                    'name': name,
                    'elevation': elevation
                }

                for var in df.columns:
                    if var in ['LATITUDE', 'LONGITUDE', 'STATION', 'DATE', 'SOURCE', 'ELEVATION', 'NAME',
                               'REPORT_TYPE', 'CALL_SIGN', 'QUALITY_CONTROL']:
                        continue

                    if df[var].dropna().apply(extract_first_number).notna().any():
                        variable_years[(lat, lon, var)].add(int(year))

            except Exception as e:
                print(f"❌ Error in {file_path}: {e}")

    result = defaultdict(dict)
    for (lat, lon, var), years in variable_years.items():
        info = station_info.get((lat, lon), {})
        key = f"{lat:.5f},{lon:.5f}"
        if key not in result[var]:
            result[var][key] = {
                'lat': lat,
                'lon': lon,
                'id': info.get('id'),
                'name': info.get('name'),
                'elevation': info.get('elevation'),
                'variables': {}
            }
        result[var][key]['variables'][var] = {
            'count_years': len(years),
            'year_ranges': group_years(years)
        }

    for var in result:
        result[var] = list(result[var].values())

    cached_data = result
    return cached_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(load_station_data())

if __name__ == '__main__':
    print("🔄 Preloading station data into memory...")
    load_station_data()
    print("✅ Data cached. Starting Flask app...")
    app.run(debug=True)
