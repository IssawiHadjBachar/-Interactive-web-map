# Variable Map Viewer 🌐

This web application allows users to interactively visualize weather station data on a Leaflet map, categorized by environmental variables (e.g., temperature, precipitation, wind). It uses colored circle markers to represent stations, with popups displaying variable availability and metadata (station name, elevation, lat/lon, etc.).

## 🧠 Features

- Interactive Leaflet map with variable toggles  
- Colored markers per selected variable  
- Station popups showing:  
  - Variable year count  
  - Operational year ranges  
  - Metadata (ID, name, elevation, location)  
- Exportable map image using `Leaflet.easyPrint`  
- Data preprocessing with Flask backend (Pandas, JSON)  
- Fast response with in-memory caching (`cached_data`)

## 🗂 Folder Structure
project/
│
├── static/
│ └── js/
│ └── script.js # Front-end Leaflet + EasyPrint logic
├── templates/
│ └── index.html # Main HTML page
├── app.py # Flask backend with data loading
├── .gitignore # Lists folders like data/ to be ignored by Git
└── data/ # ❌ Not pushed to GitHub — contains station CSVs per year

⚠️ **Note:** The `data/` folder is excluded from Git using `.gitignore`. It must be manually added on your local machine to run the app.

## 📦 Installation

1. **Clone the repo:**
   git clone https://github.com/IssawiHadjBachar/-Interactive-web-map.git
   cd -Interactive-web-map

Prepare your data/ directory:

Place your structured data in a folder like this:

data/
  ├── 2000/
  │    ├── 7021230.csv
  │    └── ...
  ├── 2001/
  └── ...
Run the app:

python app.py
Then open your browser at: http://127.0.0.1:5000

🧾 Notes
The backend parses all .csv files by year and station ID.
Each variable shows:
Count of available years
Grouped year ranges (e.g., 2000–2003, 2005)
Leaflet EasyPrint allows users to export the map view as an image.
