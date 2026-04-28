const COLORS = {
  terracotta: "#b85042",
  sage: "#a7beae",
  sand: "#e7e8d1",
  dark: "#2f2925",
  blue: "#426a78",
  gold: "#c99b3f",
  muted: "#657176",
};

const schemes = {
  Base: [0.4, 0.4, 0.2],
  "Hazard-led": [0.6, 0.25, 0.15],
  "Exposure-led": [0.25, 0.6, 0.15],
};

const facilityTypes = [
  ["hospital", "Hospital", COLORS.terracotta],
  ["school", "School", COLORS.sage],
  ["fire_ems", "Fire/EMS", COLORS.blue],
  ["police", "Police", COLORS.gold],
];

const counties = [
  {
    name: "Lehigh",
    bbox: [-75.84, 40.402, -75.354, 40.789],
    area: 906,
    pop: 374557,
    karst: 8300,
    loss: 8.7,
    facilities: { hospital: 6, school: 75, fire_ems: 38, police: 14 },
    buffers: { "100m": 15, "250m": 18, "500m": 25, outside: 75 },
  },
  {
    name: "Berks",
    bbox: [-76.246, 40.197, -75.604, 40.581],
    area: 2261,
    pop: 428849,
    karst: 11250,
    loss: 10.9,
    facilities: { hospital: 4, school: 97, fire_ems: 72, police: 28 },
    buffers: { "100m": 17, "250m": 28, "500m": 38, outside: 118 },
  },
  {
    name: "Bucks",
    bbox: [-75.477, 40.118, -74.694, 40.609],
    area: 1597,
    pop: 646538,
    karst: 6050,
    loss: 8.2,
    facilities: { hospital: 7, school: 110, fire_ems: 65, police: 35 },
    buffers: { "100m": 12, "250m": 20, "500m": 24, outside: 161 },
  },
  {
    name: "Montgomery",
    bbox: [-75.694, 40.08, -75.09, 40.451],
    area: 1265,
    pop: 856553,
    karst: 7320,
    loss: 12.4,
    facilities: { hospital: 9, school: 160, fire_ems: 88, police: 42 },
    buffers: { "100m": 24, "250m": 31, "500m": 37, outside: 207 },
  },
  {
    name: "Chester",
    bbox: [-76.058, 39.72, -75.42, 40.262],
    area: 1944,
    pop: 545823,
    karst: 8840,
    loss: 9.8,
    facilities: { hospital: 5, school: 92, fire_ems: 70, police: 30 },
    buffers: { "100m": 18, "250m": 27, "500m": 32, outside: 120 },
  },
];

const muniCells = [
  { label: "Pottstown cell", county: "Montgomery", h: 0.68, e: 1, c: 0.96 },
  { label: "Reading cell", county: "Berks", h: 1, e: 0.72, c: 0.64 },
  { label: "West Chester cell", county: "Chester", h: 0.82, e: 0.62, c: 0.72 },
  { label: "Allentown cell", county: "Lehigh", h: 0.76, e: 0.58, c: 0.68 },
  { label: "Doylestown cell", county: "Bucks", h: 0.5, e: 0.7, c: 0.76 },
  { label: "Phoenixville cell", county: "Chester", h: 0.58, e: 0.66, c: 0.7 },
  { label: "Lansdale cell", county: "Montgomery", h: 0.46, e: 0.74, c: 0.78 },
  { label: "Boyertown cell", county: "Berks", h: 0.72, e: 0.48, c: 0.52 },
];

let selectedCounty = "All";
let selectedBuffer = 500;
let selectedScheme = "Base";
let activeTab = "overview";
const activeTypes = new Set(facilityTypes.map(([key]) => key));

const formatNumber = new Intl.NumberFormat("en-US");
const formatPct = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

function totalFacilities(county) {
  return Object.values(county.facilities).reduce((sum, value) => sum + value, 0);
}

function filteredFacilities(county) {
  return facilityTypes.reduce((sum, [key]) => {
    return activeTypes.has(key) ? sum + county.facilities[key] : sum;
  }, 0);
}

function activeShare(county) {
  const total = totalFacilities(county);
  return total ? filteredFacilities(county) / total : 0;
}

function exposedAtBuffer(county) {
  const raw =
    county.buffers["100m"] +
    (selectedBuffer >= 250 ? county.buffers["250m"] : 0) +
    (selectedBuffer >= 500 ? county.buffers["500m"] : 0);
  return Math.round(raw * activeShare(county));
}

function activeCounties() {
  return selectedCounty === "All"
    ? counties
    : counties.filter((county) => county.name === selectedCounty);
}

function currentWeights() {
  if (selectedScheme !== "Custom") return schemes[selectedScheme];
  const h = Number(document.querySelector("#hazardWeight")?.value || 40);
  const e = Number(document.querySelector("#exposureWeight")?.value || 40);
  const c = Number(document.querySelector("#criticalWeight")?.value || 20);
  const total = h + e + c || 1;
  return [h / total, e / total, c / total];
}

function scoreCell(cell) {
  const [h, e, c] = currentWeights();
  return Math.round(1000 * (h * cell.h + e * cell.e + c * cell.c)) / 10;
}

function svgEl(tag, attrs = {}, children = []) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  children.forEach((child) => {
    el.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  });
  return el;
}

function renderControls() {
  const countySelect = document.querySelector("#countySelect");
  ["All", ...counties.map((county) => county.name)].forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name === "All" ? "All counties" : name;
    countySelect.appendChild(option);
  });
  countySelect.addEventListener("change", (event) => {
    selectedCounty = event.target.value;
    render();
  });

  document.querySelector("#bufferSelect").addEventListener("change", (event) => {
    selectedBuffer = Number(event.target.value);
    render();
  });

  document.querySelectorAll(".segment").forEach((button) => {
    button.addEventListener("click", () => {
      selectedScheme = button.dataset.scheme;
      document
        .querySelectorAll(".segment")
        .forEach((segment) => segment.classList.toggle("active", segment === button));
      updateWeightSliders();
      render();
    });
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      activeTab = tab.dataset.tab;
      document.querySelectorAll(".tab").forEach((item) => {
        item.classList.toggle("active", item === tab);
      });
      document.querySelectorAll(".tab-view").forEach((view) => {
        view.classList.toggle("active", view.dataset.view === activeTab);
      });
      render();
    });
  });

  renderTypeFilter();
  ["hazardWeight", "exposureWeight", "criticalWeight"].forEach((id) => {
    document.querySelector(`#${id}`)?.addEventListener("input", () => {
      selectedScheme = "Custom";
      document.querySelectorAll(".segment").forEach((segment) => segment.classList.remove("active"));
      render();
    });
  });
  ["hazardScale", "damageScale", "responseScale"].forEach((id) => {
    document.querySelector(`#${id}`)?.addEventListener("input", renderScenario);
  });
}

function renderTypeFilter() {
  const target = document.querySelector("#typeFilter");
  if (!target) return;
  target.innerHTML = "";
  facilityTypes.forEach(([key, label, color]) => {
    const row = document.createElement("label");
    row.className = "check-row";
    row.innerHTML = `
      <span style="color:${color}">${label}</span>
      <input type="checkbox" value="${key}" checked>
    `;
    row.querySelector("input").addEventListener("change", (event) => {
      if (event.target.checked) {
        activeTypes.add(key);
      } else {
        activeTypes.delete(key);
      }
      if (activeTypes.size === 0) {
        activeTypes.add(key);
        event.target.checked = true;
      }
      render();
    });
    target.appendChild(row);
  });
}

function updateWeightSliders() {
  if (selectedScheme === "Custom") return;
  const [h, e, c] = schemes[selectedScheme];
  const values = [h, e, c].map((value) => Math.round(value * 100));
  const ids = ["hazardWeight", "exposureWeight", "criticalWeight"];
  ids.forEach((id, index) => {
    const input = document.querySelector(`#${id}`);
    if (input) input.value = values[index];
  });
}

function renderMetrics() {
  const rows = activeCounties();
  const facilities = rows.reduce((sum, county) => sum + filteredFacilities(county), 0);
  const karst = rows.reduce((sum, county) => sum + county.karst, 0);
  const pop = rows.reduce((sum, county) => sum + county.pop, 0);
  const exposed = rows.reduce((sum, county) => sum + exposedAtBuffer(county), 0);
  document.querySelector("#metricCounties").textContent = rows.length;
  document.querySelector("#metricKarst").textContent = formatNumber.format(karst);
  document.querySelector("#metricFacilities").textContent = formatNumber.format(facilities);
  document.querySelector("#metricExposed").textContent = formatNumber.format(exposed);
  document.querySelector("#metricPopulation").textContent =
    pop >= 1000000 ? `${(pop / 1000000).toFixed(2)}M` : formatNumber.format(pop);
  document.querySelector("#metricBufferNote").textContent = `within ${selectedBuffer} m`;
  document.querySelector("#selectedBadge").textContent =
    selectedCounty === "All" ? "All counties" : selectedCounty;
}

function renderMap() {
  const wrap = document.querySelector("#mapViz");
  const width = 820;
  const height = 560;
  const padding = 42;
  const allBboxes = counties.map((county) => county.bbox);
  const minLon = Math.min(...allBboxes.map((bbox) => bbox[0]));
  const minLat = Math.min(...allBboxes.map((bbox) => bbox[1]));
  const maxLon = Math.max(...allBboxes.map((bbox) => bbox[2]));
  const maxLat = Math.max(...allBboxes.map((bbox) => bbox[3]));
  const scaleX = (lon) => padding + ((lon - minLon) / (maxLon - minLon)) * (width - padding * 2);
  const scaleY = (lat) => height - padding - ((lat - minLat) / (maxLat - minLat)) * (height - padding * 2);
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}`, role: "img" });

  counties.forEach((county) => {
    const [minX, minY, maxX, maxY] = county.bbox;
    const x = scaleX(minX);
    const y = scaleY(maxY);
    const w = scaleX(maxX) - scaleX(minX);
    const h = scaleY(minY) - scaleY(maxY);
    const isSelected = selectedCounty === "All" || selectedCounty === county.name;
    const exposure = exposedAtBuffer(county);
    svg.appendChild(
      svgEl("rect", {
        x,
        y,
        width: w,
        height: h,
        rx: 5,
        class: `county-shape ${isSelected && selectedCounty !== "All" ? "selected" : ""}`,
        opacity: isSelected ? 1 : 0.18,
      })
    );
    svg.appendChild(
      svgEl("text", { x: x + 8, y: y + 19, class: "map-label", opacity: isSelected ? 1 : 0.38 }, [
        county.name,
      ])
    );

    const cx = x + w * 0.58;
    const cy = y + h * 0.56;
    const hazardR = 10 + (county.karst / 11250) * 31;
    const exposureR = 7 + (exposure / 92) * 20;
    svg.appendChild(
      svgEl("circle", {
        cx,
        cy,
        r: hazardR,
        fill: COLORS.terracotta,
        opacity: isSelected ? 0.28 : 0.08,
      })
    );
    svg.appendChild(
      svgEl("circle", {
        cx: cx + 22,
        cy: cy - 10,
        r: exposureR,
        fill: COLORS.blue,
        opacity: isSelected ? 0.45 : 0.12,
      })
    );
  });

  svg.appendChild(
    svgEl("text", { x: 42, y: 532, class: "axis-label" }, [
      `Circle size: mapped karst density and active facilities within ${selectedBuffer} m`,
    ])
  );
  wrap.replaceChildren(svg);
}

function horizontalBars(rows, maxValue, options = {}) {
  const width = 620;
  const rowH = options.rowH || 40;
  const height = 34 + rows.length * rowH;
  const labelWidth = options.labelWidth || 128;
  const barWidth = options.barWidth || 350;
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });
  rows.forEach((row, index) => {
    const y = 28 + index * rowH;
    const barW = maxValue ? (row.value / maxValue) * barWidth : 0;
    const overlayW = maxValue ? ((row.secondary || row.value) / maxValue) * barWidth : 0;
    svg.appendChild(svgEl("text", { x: 0, y: y + 14, class: "bar-label" }, [row.label]));
    svg.appendChild(svgEl("rect", { x: labelWidth, y, width: barWidth, height: 18, rx: 4, fill: "#edf0ea" }));
    svg.appendChild(
      svgEl("rect", { x: labelWidth, y, width: barW, height: 18, rx: 4, fill: row.color || COLORS.sage })
    );
    svg.appendChild(
      svgEl("rect", {
        x: labelWidth,
        y,
        width: overlayW,
        height: 18,
        rx: 4,
        fill: row.secondaryColor || COLORS.terracotta,
      })
    );
    svg.appendChild(svgEl("text", { x: labelWidth + barWidth + 14, y: y + 14, class: "bar-value" }, [
      row.valueText,
    ]));
  });
  return svg;
}

function renderCountyBars() {
  const rows = activeCounties();
  const maxValue = Math.max(...counties.map((county) => totalFacilities(county)));
  const chartRows = rows.map((county) => {
    const total = filteredFacilities(county);
    const exposed = exposedAtBuffer(county);
    return {
      label: county.name,
      value: total,
      secondary: exposed,
      color: COLORS.sage,
      secondaryColor: COLORS.terracotta,
      valueText: `${exposed}/${total} (${formatPct.format(exposed / total || 0)})`,
    };
  });
  document.querySelector("#countyBars")?.replaceChildren(horizontalBars(chartRows, maxValue));
  document.querySelector("#exposureBars")?.replaceChildren(horizontalBars(chartRows, maxValue, { rowH: 48 }));
}

function renderFacilityMix() {
  const rows = activeCounties();
  const totals = Object.fromEntries(facilityTypes.map(([key]) => [key, 0]));
  rows.forEach((county) => {
    facilityTypes.forEach(([key]) => {
      if (activeTypes.has(key)) totals[key] += county.facilities[key];
    });
  });
  const all = Object.values(totals).reduce((sum, value) => sum + value, 0);
  const max = Math.max(1, ...Object.values(totals));
  const chartRows = facilityTypes
    .filter(([key]) => activeTypes.has(key))
    .map(([key, label, color]) => ({
      label,
      value: totals[key],
      secondary: totals[key],
      color,
      secondaryColor: color,
      valueText: `${totals[key]} (${formatPct.format(totals[key] / all || 0)})`,
    }));
  document.querySelector("#facilityMix")?.replaceChildren(horizontalBars(chartRows, max));
}

function renderCountyProfile() {
  const target = document.querySelector("#countyProfile");
  if (!target) return;
  const rows = activeCounties();
  const facilities = rows.reduce((sum, county) => sum + filteredFacilities(county), 0);
  const exposed = rows.reduce((sum, county) => sum + exposedAtBuffer(county), 0);
  const area = rows.reduce((sum, county) => sum + county.area, 0);
  const karst = rows.reduce((sum, county) => sum + county.karst, 0);
  target.innerHTML = `
    <div><b>Karst density</b><span>${(karst / area).toFixed(2)} mapped features per km2</span></div>
    <div><b>Exposure share</b><span>${formatPct.format(exposed / facilities || 0)} of active facilities within ${selectedBuffer} m</span></div>
    <div><b>Study role</b><span>${selectedCounty === "All" ? "regional comparison across five counties" : `${selectedCounty} county profile`}</span></div>
  `;
}

function renderBufferDonut() {
  const rows = activeCounties();
  const totals = { "100m": 0, "250m": 0, "500m": 0, outside: 0 };
  rows.forEach((county) => {
    const share = activeShare(county);
    Object.keys(totals).forEach((key) => {
      totals[key] += Math.round(county.buffers[key] * share);
    });
  });
  const data = [
    { label: "100m", value: totals["100m"], color: COLORS.terracotta },
    { label: "250m", value: totals["250m"], color: COLORS.gold },
    { label: "500m", value: totals["500m"], color: COLORS.sage },
    { label: "outside", value: totals.outside, color: COLORS.blue },
  ];
  const total = data.reduce((sum, item) => sum + item.value, 0) || 1;
  const width = 360;
  const height = 300;
  const cx = 130;
  const cy = 140;
  const r = 82;
  const stroke = 30;
  const circumference = 2 * Math.PI * r;
  let offset = 0;
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });
  svg.appendChild(svgEl("circle", { cx, cy, r, fill: "none", stroke: "#edf0ea", "stroke-width": stroke }));
  data.forEach((item) => {
    const length = (item.value / total) * circumference;
    svg.appendChild(
      svgEl("circle", {
        cx,
        cy,
        r,
        fill: "none",
        stroke: item.color,
        "stroke-width": stroke,
        "stroke-dasharray": `${length} ${circumference - length}`,
        "stroke-dashoffset": -offset,
        transform: `rotate(-90 ${cx} ${cy})`,
      })
    );
    offset += length;
  });
  svg.appendChild(svgEl("text", { x: cx, y: cy - 4, "text-anchor": "middle", class: "bar-label" }, [
    formatNumber.format(total),
  ]));
  svg.appendChild(svgEl("text", { x: cx, y: cy + 16, "text-anchor": "middle", class: "axis-label" }, [
    "active facilities",
  ]));
  data.forEach((item, index) => {
    const y = 76 + index * 34;
    svg.appendChild(svgEl("rect", { x: 250, y: y - 12, width: 13, height: 13, rx: 3, fill: item.color }));
    svg.appendChild(svgEl("text", { x: 270, y, class: "bar-value" }, [`${item.label}: ${item.value}`]));
  });
  document.querySelector("#bufferDonut")?.replaceChildren(svg);
}

function renderKhi() {
  const countyFilter = selectedCounty === "All" ? null : selectedCounty;
  const rows = muniCells
    .filter((cell) => !countyFilter || cell.county === countyFilter)
    .map((cell) => ({ ...cell, score: scoreCell(cell) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 8);
  const target = document.querySelector("#khiList");
  if (!target) return;
  target.innerHTML = "";
  rows.forEach((row, index) => {
    const item = document.createElement("div");
    item.className = "khi-row";
    item.innerHTML = `
      <div class="rank">${index + 1}</div>
      <div>
        <strong>${row.label}</strong>
        <span>${row.county} - ${selectedScheme}</span>
      </div>
      <div class="khi-score">${row.score.toFixed(1)}</div>
    `;
    target.appendChild(item);
  });
  const [h, e, c] = currentWeights();
  const readout = document.querySelector("#weightReadout");
  if (readout) {
    readout.innerHTML = `
      Active scheme: ${selectedScheme}<br>
      Hazard ${(h * 100).toFixed(0)}% / Exposure ${(e * 100).toFixed(0)}% / Criticality ${(c * 100).toFixed(0)}%
    `;
  }
}

function renderExposureNarrative() {
  const rows = activeCounties();
  const facilities = rows.reduce((sum, county) => sum + filteredFacilities(county), 0);
  const exposed = rows.reduce((sum, county) => sum + exposedAtBuffer(county), 0);
  const typeNames = facilityTypes
    .filter(([key]) => activeTypes.has(key))
    .map(([, label]) => label.toLowerCase())
    .join(", ");
  const target = document.querySelector("#exposureNarrative");
  if (target) {
    target.textContent = `${formatNumber.format(exposed)} of ${formatNumber.format(
      facilities
    )} active ${typeNames} facilities are inside the ${selectedBuffer} m screening buffer for ${
      selectedCounty === "All" ? "the full study area" : selectedCounty
    }.`;
  }
}

function renderScenario() {
  const hazard = Number(document.querySelector("#hazardScale")?.value || 100) / 100;
  const damage = Number(document.querySelector("#damageScale")?.value || 100) / 100;
  const response = Number(document.querySelector("#responseScale")?.value || 35) / 100;
  const rows = activeCounties();
  const responseCredit = 1 - response * 0.35;
  const scenarioRows = rows.map((county) => {
    const share = activeShare(county);
    return {
      label: county.name,
      value: county.loss * share * hazard * damage * responseCredit,
    };
  });
  const total = scenarioRows.reduce((sum, row) => sum + row.value, 0);
  const max = Math.max(1, ...scenarioRows.map((row) => row.value));
  const chartRows = scenarioRows.map((row) => ({
    label: row.label,
    value: row.value,
    secondary: row.value,
    color: COLORS.gold,
    secondaryColor: COLORS.gold,
    valueText: `${row.value.toFixed(1)} index`,
  }));
  document.querySelector("#lossBars")?.replaceChildren(horizontalBars(chartRows, max, { rowH: 48 }));
  renderGauge(total, hazard, damage, response);
}

function renderGauge(total, hazard, damage, response) {
  const target = document.querySelector("#scenarioGauge");
  if (!target) return;
  const width = 340;
  const height = 190;
  const percent = Math.min(total / 55, 1);
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });
  svg.appendChild(svgEl("path", { d: "M 50 150 A 120 120 0 0 1 290 150", fill: "none", stroke: "#edf0ea", "stroke-width": 28, "stroke-linecap": "round" }));
  svg.appendChild(svgEl("path", { d: "M 50 150 A 120 120 0 0 1 290 150", fill: "none", stroke: COLORS.terracotta, "stroke-width": 28, "stroke-linecap": "round", "stroke-dasharray": `${percent * 377} 377` }));
  svg.appendChild(svgEl("text", { x: 170, y: 124, "text-anchor": "middle", class: "bar-label" }, [
    `${total.toFixed(1)} loss index`,
  ]));
  svg.appendChild(svgEl("text", { x: 170, y: 146, "text-anchor": "middle", class: "axis-label" }, [
    `H ${(hazard * 100).toFixed(0)} / D ${(damage * 100).toFixed(0)} / R ${(response * 100).toFixed(0)}`,
  ]));
  target.replaceChildren(svg);
  const headline = document.querySelector("#scenarioHeadline");
  if (headline) {
    headline.textContent = total > 36 ? "High stress case" : total > 22 ? "Moderate stress case" : "Lower stress case";
  }
  const text = document.querySelector("#scenarioText");
  if (text) {
    text.textContent =
      "The scenario index scales the relative loss proxy with hazard intensity, damage severity, active facility filters, and response capacity.";
  }
}

function renderAll() {
  renderMetrics();
  renderMap();
  renderCountyBars();
  renderFacilityMix();
  renderCountyProfile();
  renderBufferDonut();
  renderKhi();
  renderExposureNarrative();
  renderScenario();
}

function render() {
  renderAll();
}

renderControls();
updateWeightSliders();
render();
