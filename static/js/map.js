let map = L.map('map').setView([45, -73], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// EasyPrint control setup
const printControl = L.easyPrint({
  title: 'Download',
  position: 'topleft',
  exportOnly: true,
  hideControlContainer: true,
  filename: 'variable_map'
}).addTo(map);

// Trigger EasyPrint manually from the button
document.getElementById('print-map').addEventListener('click', function () {
  printControl.printMap('CurrentSize', 'variable_map');
});

let variableLayers = {};
let stationLayers = {};

fetch('/data')
  .then(response => response.json())
  .then(data => {
    const controlsDiv = document.getElementById('controls');

    Object.keys(data).forEach((variable, index) => {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = variable;
      checkbox.dataset.color = getColor(index);
      checkbox.addEventListener('change', () => toggleVariable(variable, data[variable], checkbox.checked, checkbox.dataset.color));

      const label = document.createElement('label');
      label.htmlFor = variable;
      label.style.marginRight = "15px";
      label.innerHTML = `<span style="color:${checkbox.dataset.color}; font-weight:600;">■</span> ${variable}`;

      controlsDiv.appendChild(checkbox);
      controlsDiv.appendChild(label);
    });
  });

function toggleVariable(variable, stations, show, color) {
  if (show) {
    stations.forEach(station => {
      const key = `${station.lat.toFixed(5)},${station.lon.toFixed(5)}`;
      if (!stationLayers[key]) {
        const marker = L.circleMarker([station.lat, station.lon], {
          radius: 8,
          fillColor: color,
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.6
        }).addTo(map);

        marker.bindPopup(() => generatePopupContent(stationLayers[key]));

        stationLayers[key] = {
          lat: station.lat,
          lon: station.lon,
          id: station.id,
          name: station.name,
          elevation: station.elevation,
          marker: marker,
          variables: {}
        };
      }

      stationLayers[key].variables[variable] = station.variables[variable];
      stationLayers[key].marker.setPopupContent(generatePopupContent(stationLayers[key]));
    });
  } else {
    Object.keys(stationLayers).forEach(key => {
      delete stationLayers[key].variables[variable];
      if (Object.keys(stationLayers[key].variables).length === 0) {
        map.removeLayer(stationLayers[key].marker);
        delete stationLayers[key];
      } else {
        stationLayers[key].marker.setPopupContent(generatePopupContent(stationLayers[key]));
      }
    });
  }
}

function generatePopupContent(station) {
  let html = `<strong>Variables:</strong><br>`;
  for (const [varName, data] of Object.entries(station.variables)) {
    html += `- <strong>${varName}</strong>: ${data.count_years} years (${data.year_ranges.join(', ')})<br>`;
  }
  html += `
    <br><strong>ID:</strong> ${station.id || 'N/A'}<br>
    <strong>Name:</strong> ${station.name || 'N/A'}<br>
    <strong>Elevation:</strong> ${station.elevation || 'N/A'} m<br>
    <strong>Lat:</strong> ${station.lat.toFixed(2)}, <strong>Lon:</strong> ${station.lon.toFixed(2)}
  `;
  return html;
}

function getColor(index) {
  const colors = ["blue", "green", "red", "purple", "orange", "brown", "teal", "pink", "gray"];
  return colors[index % colors.length];
}
