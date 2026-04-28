const COLORS = {
  terracotta: "#b85042",
  sage: "#a7beae",
  sand: "#e7e8d1",
  dark: "#2f2925",
  blue: "#426a78",
  gold: "#c99b3f",
  muted: "#657176",
};

const STUDY_TOTALS = {
  counties: 5,
  karst: 30623,
  hospitals: 42,
  structures: 1675,
  facilities: 1717,
  municipalities: 287,
  exposed1km: 380,
};

const schemes = {
  Base: [0.4, 0.4, 0.2],
  "Hazard-led": [0.6, 0.25, 0.15],
  "Exposure-led": [0.25, 0.6, 0.15],
};

const counties = [
  {
    name: "Berks",
    bbox: [-76.246, 40.197, -75.604, 40.581],
    area: 2242.1,
    pop: 428849,
    karst: 16294,
    density: 7.27,
    facilities: 301,
    hospitals: 7,
    exposed1km: 158,
    hospitalExposed: 5,
    loss: 11.65,
  },
  {
    name: "Lehigh",
    bbox: [-75.84, 40.402, -75.354, 40.789],
    area: 902.3,
    pop: 374557,
    karst: 10138,
    density: 11.24,
    facilities: 215,
    hospitals: 5,
    exposed1km: 116,
    hospitalExposed: 3,
    loss: 9.6,
  },
  {
    name: "Chester",
    bbox: [-76.058, 39.72, -75.42, 40.262],
    area: 1967.7,
    pop: 545823,
    karst: 2536,
    density: 1.29,
    facilities: 331,
    hospitals: 7,
    exposed1km: 63,
    hospitalExposed: 2,
    loss: 4.03,
  },
  {
    name: "Bucks",
    bbox: [-75.477, 40.118, -74.694, 40.609],
    area: 1611.2,
    pop: 646538,
    karst: 636,
    density: 0.39,
    facilities: 371,
    hospitals: 8,
    exposed1km: 3,
    hospitalExposed: 0,
    loss: 0.39,
  },
  {
    name: "Montgomery",
    bbox: [-75.694, 40.08, -75.09, 40.451],
    area: 1262.4,
    pop: 856553,
    karst: 354,
    density: 0.28,
    facilities: 499,
    hospitals: 15,
    exposed1km: 40,
    hospitalExposed: 1,
    loss: 1.82,
  },
];

const facilityTypes = [
  ["hospital", "Hospital", COLORS.terracotta],
  ["fire_ems", "Fire/EMS", COLORS.blue],
  ["police", "Police", COLORS.gold],
  ["school", "School", COLORS.sage],
];

const exposureByTypeRing = {
  hospital: { "100": 2, "250": 2, "500": 5, "1000": 2 },
  fire_ems: { "100": 13, "250": 23, "500": 36, "1000": 34 },
  police: { "100": 1, "250": 7, "500": 12, "1000": 23 },
  school: { "100": 56, "250": 62, "500": 54, "1000": 48 },
};

const hospitals = [
  ["Lehigh Valley Hospital", "Lehigh", "Allentown", 57],
  ["Tower Behavioral Health", "Berks", "Reading", 72],
  ["Surgical Institute of Reading", "Berks", "Wyomissing", 111],
  ["Good Shepherd Specialty Hospital", "Lehigh", "Bethlehem", 130],
  ["Wernersville State Hospital", "Berks", "Wernersville", 273],
  ["St. Luke's Hospital Bethlehem", "Lehigh", "Bethlehem", 294],
  ["Saint John Vianney Hospital", "Chester", "Downingtown", 303],
  ["Penn State Health St. Joseph", "Berks", "Reading", 333],
  ["VETERANS AFFAIRS MEDICAL CENTER COATESVILLE", "Chester", "Coatesville", 442],
  ["Reading Hospital", "Berks", "West Reading", 837],
  ["Holy Redeemer Hospital", "Montgomery", "Meadowbrook", 875],
];

const khiRows = [
  { label: "Allentown", county: "Lehigh", karst: 349, exposed: 45, base: 64.4, ranks: [1, 6, 1] },
  { label: "Hanover", county: "Lehigh", karst: 787, exposed: 5, base: 48.0, ranks: [2, 1, 3] },
  { label: "Maxatawny", county: "Berks", karst: 3407, exposed: 6, base: 38.3, ranks: [3, 5, 4] },
  { label: "Lyons", county: "Berks", karst: 58, exposed: 2, base: 36.6, ranks: [4, 2, 11] },
  { label: "Whitehall", county: "Lehigh", karst: 346, exposed: 18, base: 34.8, ranks: [5, 17, 2] },
  { label: "Lower Macungie", county: "Lehigh", karst: 2016, exposed: 0, base: 33.9, ranks: [6, 3, 14] },
  { label: "Richmond", county: "Berks", karst: 2462, exposed: 6, base: 33.8, ranks: [7, 9, 7] },
  { label: "Macungie", county: "Lehigh", karst: 117, exposed: 0, base: 33.5, ranks: [8, 4, 15] },
  { label: "Riegelsville", county: "Bucks", karst: 65, exposed: 1, base: 31.4, ranks: [9, 7, 20] },
  { label: "Ontelaunee", county: "Berks", karst: 981, exposed: 4, base: 30.6, ranks: [10, 10, 12] },
  { label: "South Whitehall", county: "Lehigh", karst: 1248, exposed: 7, base: 30.2, ranks: [11, 11, 10] },
  { label: "Upper Macungie", county: "Lehigh", karst: 2990, exposed: 0, base: 28.8, ranks: [12, 8, 24] },
  { label: "Muhlenberg", county: "Berks", karst: 688, exposed: 10, base: 26.9, ranks: [13, 18, 9] },
  { label: "Topton", county: "Berks", karst: 70, exposed: 2, base: 26.3, ranks: [14, 12, 23] },
  { label: "Fleetwood", county: "Berks", karst: 59, exposed: 5, base: 26.1, ranks: [15, 13, 19] },
];

let selectedCounty = "All";
let selectedBuffer = 1000;
let selectedScheme = "Base";
const activeTypes = new Set(facilityTypes.map(([key]) => key));

const formatNumber = new Intl.NumberFormat("en-US");
const formatPct = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

const seededRandom = (() => {
  let seed = 92842;
  return () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  };
})();

const motionParticles = Array.from({ length: 210 }, (_, index) => ({
  angle: seededRandom() * Math.PI * 2,
  radius: 38 + seededRandom() * 245,
  speed: 0.18 + seededRandom() * 0.58,
  depth: seededRandom(),
  size: 0.9 + seededRandom() * 2.3,
  drift: seededRandom() * Math.PI * 2,
  county: counties[index % counties.length].name,
}));

const motionFacilities = [
  { county: "Lehigh", x: 0.38, y: 0.38, pulse: 0.0 },
  { county: "Berks", x: 0.27, y: 0.58, pulse: 0.35 },
  { county: "Chester", x: 0.39, y: 0.76, pulse: 0.7 },
  { county: "Montgomery", x: 0.54, y: 0.58, pulse: 1.1 },
  { county: "Bucks", x: 0.66, y: 0.5, pulse: 1.45 },
];

function activeCounties() {
  return selectedCounty === "All"
    ? counties
    : counties.filter((county) => county.name === selectedCounty);
}

function ringKeysForBuffer() {
  const keys = ["100"];
  if (selectedBuffer >= 250) keys.push("250");
  if (selectedBuffer >= 500) keys.push("500");
  if (selectedBuffer >= 1000) keys.push("1000");
  return keys;
}

function activeExposureTotalByType(typeKey, buffer = selectedBuffer) {
  const keys = ["100"];
  if (buffer >= 250) keys.push("250");
  if (buffer >= 500) keys.push("500");
  if (buffer >= 1000) keys.push("1000");
  return keys.reduce((sum, key) => sum + exposureByTypeRing[typeKey][key], 0);
}

function activeExposureScale() {
  const all = facilityTypes.reduce((sum, [key]) => sum + activeExposureTotalByType(key), 0);
  const selected = facilityTypes.reduce((sum, [key]) => {
    return activeTypes.has(key) ? sum + activeExposureTotalByType(key) : sum;
  }, 0);
  return all ? selected / all : 1;
}

function exposedAtBuffer(county) {
  const totalAtBuffer = facilityTypes.reduce((sum, [key]) => sum + activeExposureTotalByType(key), 0);
  const oneKmTotal = STUDY_TOTALS.exposed1km;
  const bufferScale = oneKmTotal ? totalAtBuffer / oneKmTotal : 1;
  return Math.round(county.exposed1km * bufferScale * activeExposureScale());
}

function selectedFacilities(county) {
  return county.facilities;
}

function currentWeights() {
  if (selectedScheme !== "Custom") return schemes[selectedScheme];
  const h = Number(document.querySelector("#hazardWeight")?.value || 40);
  const e = Number(document.querySelector("#exposureWeight")?.value || 40);
  const c = Number(document.querySelector("#criticalWeight")?.value || 20);
  const total = h + e + c || 1;
  return [h / total, e / total, c / total];
}

function derivedKhi(row) {
  if (selectedScheme === "Base") return row.base;
  if (selectedScheme === "Hazard-led") {
    return Math.max(0, row.base + (row.ranks[0] - row.ranks[1]) * 1.2);
  }
  if (selectedScheme === "Exposure-led") {
    return Math.max(0, row.base + (row.ranks[0] - row.ranks[2]) * 1.2);
  }
  const [h, e, c] = currentWeights();
  const hNorm = row.karst / 3407;
  const eNorm = row.exposed / 45;
  const cNorm = Math.min(1, 0.6 * eNorm + 0.4 * (row.base / 64.4));
  return 100 * (h * hNorm + e * eNorm + c * cNorm);
}

function svgEl(tag, attrs = {}, children = []) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  children.forEach((child) => {
    el.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  });
  return el;
}

function canvasRoundRect(ctx, x, y, width, height, radius) {
  if (typeof ctx.roundRect === "function") {
    ctx.roundRect(x, y, width, height, radius);
    return;
  }
  const r = Math.min(radius, width / 2, height / 2);
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + width - r, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + r);
  ctx.lineTo(x + width, y + height - r);
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  ctx.lineTo(x + r, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
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
      document.querySelectorAll(".segment").forEach((segment) => {
        segment.classList.toggle("active", segment === button);
      });
      updateWeightSliders();
      render();
    });
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => {
        item.classList.toggle("active", item === tab);
      });
      document.querySelectorAll(".tab-view").forEach((view) => {
        view.classList.toggle("active", view.dataset.view === tab.dataset.tab);
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
      if (event.target.checked) activeTypes.add(key);
      else activeTypes.delete(key);
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
  const ids = ["hazardWeight", "exposureWeight", "criticalWeight"];
  schemes[selectedScheme].forEach((value, index) => {
    const input = document.querySelector(`#${ids[index]}`);
    if (input) input.value = Math.round(value * 100);
  });
}

function renderMetrics() {
  const rows = activeCounties();
  const facilities = rows.reduce((sum, county) => sum + selectedFacilities(county), 0);
  const karst =
    selectedCounty === "All" ? STUDY_TOTALS.karst : rows.reduce((sum, county) => sum + county.karst, 0);
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
    const hazardR = 10 + (county.density / 11.24) * 34;
    const exposureR = 7 + (exposure / 158) * 24;
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
      `Circle size: karst density and facilities within ${selectedBuffer} m`,
    ])
  );
  wrap.replaceChildren(svg);
}

function horizontalBars(rows, maxValue, options = {}) {
  const width = 640;
  const rowH = options.rowH || 40;
  const height = 34 + rows.length * rowH;
  const labelWidth = options.labelWidth || 135;
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
  const maxValue = Math.max(...counties.map((county) => county.facilities));
  const chartRows = rows.map((county) => {
    const exposed = exposedAtBuffer(county);
    return {
      label: county.name,
      value: county.facilities,
      secondary: exposed,
      color: COLORS.sage,
      secondaryColor: COLORS.terracotta,
      valueText: `${exposed}/${county.facilities} (${formatPct.format(exposed / county.facilities)})`,
    };
  });
  document.querySelector("#countyBars")?.replaceChildren(horizontalBars(chartRows, maxValue));
  document.querySelector("#exposureBars")?.replaceChildren(horizontalBars(chartRows, maxValue, { rowH: 48 }));
}

function renderFacilityMix() {
  const chartRows = facilityTypes
    .filter(([key]) => activeTypes.has(key))
    .map(([key, label, color]) => {
      const exposed = activeExposureTotalByType(key);
      return {
        label,
        value: exposed,
        secondary: exposed,
        color,
        secondaryColor: color,
        valueText: `${exposed} exposed`,
      };
    });
  const max = Math.max(1, ...chartRows.map((row) => row.value));
  document.querySelector("#facilityMix")?.replaceChildren(horizontalBars(chartRows, max));
}

function renderCountyProfile() {
  const target = document.querySelector("#countyProfile");
  if (!target) return;
  const rows = activeCounties();
  const exposed = rows.reduce((sum, county) => sum + exposedAtBuffer(county), 0);
  const facilities = rows.reduce((sum, county) => sum + county.facilities, 0);
  const densityText =
    selectedCounty === "All"
      ? "Lehigh 11.24/km2; Berks 7.27/km2; sharp drop-off west/south"
      : `${rows[0].density.toFixed(2)} mapped karst features per km2`;
  target.innerHTML = `
    <div><b>Karst density</b><span>${densityText}</span></div>
    <div><b>Exposure share</b><span>${formatPct.format(exposed / facilities || 0)} of facilities within ${selectedBuffer} m</span></div>
    <div><b>Study role</b><span>${selectedCounty === "All" ? "regional comparison across five counties" : `${selectedCounty} county profile`}</span></div>
  `;
}

function renderBufferDonut() {
  const data = facilityTypes.map(([key, label, color]) => ({
    label,
    value: activeTypes.has(key) ? activeExposureTotalByType(key) : 0,
    color,
  }));
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
    `within ${selectedBuffer} m`,
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
  const rows = khiRows
    .filter((row) => !countyFilter || row.county === countyFilter)
    .map((row) => ({ ...row, score: derivedKhi(row) }))
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
        <span>${row.county} - karst ${formatNumber.format(row.karst)} / exposed ${row.exposed}</span>
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
  const exposed = rows.reduce((sum, county) => sum + exposedAtBuffer(county), 0);
  const facilities = rows.reduce((sum, county) => sum + county.facilities, 0);
  const selectedTypeLabels = facilityTypes
    .filter(([key]) => activeTypes.has(key))
    .map(([, label]) => label.toLowerCase())
    .join(", ");
  const target = document.querySelector("#exposureNarrative");
  if (target) {
    target.textContent = `${formatNumber.format(exposed)} of ${formatNumber.format(
      facilities
    )} facilities are inside the ${selectedBuffer} m screening buffer for ${
      selectedCounty === "All" ? "the full study area" : selectedCounty
    }. Type filter is showing ${selectedTypeLabels}.`;
  }
}

function renderHospitalTable() {
  const target = document.querySelector("#hospitalTable");
  if (!target) return;
  const rows = hospitals.filter((row) => selectedCounty === "All" || row[1] === selectedCounty);
  target.innerHTML = `
    <table class="data-table">
      <thead>
        <tr><th>Rank</th><th>Hospital</th><th>County</th><th>City</th><th>Nearest karst</th></tr>
      </thead>
      <tbody>
        ${rows
          .map(
            ([name, county, city, distance], index) =>
              `<tr><td><strong>#${index + 1}</strong></td><td>${name}</td><td>${county}</td><td>${city}</td><td><strong>${distance} m</strong></td></tr>`
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderSensitivityTable() {
  const target = document.querySelector("#sensitivityTable");
  if (!target) return;
  target.innerHTML = `
    <table class="data-table">
      <thead>
        <tr><th>Municipality</th><th>County</th><th>Base</th><th>Hazard-led</th><th>Exposure-led</th><th>Max change</th></tr>
      </thead>
      <tbody>
        ${khiRows
          .slice(0, 15)
          .map((row) => {
            const maxDelta = Math.max(...row.ranks) - Math.min(...row.ranks);
            return `<tr><td>${row.label}</td><td>${row.county}</td><td>${row.ranks[0]}</td><td>${row.ranks[1]}</td><td>${row.ranks[2]}</td><td><strong>${maxDelta}</strong></td></tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function renderScenario() {
  const hazard = Number(document.querySelector("#hazardScale")?.value || 100) / 100;
  const damage = Number(document.querySelector("#damageScale")?.value || 100) / 100;
  const response = Number(document.querySelector("#responseScale")?.value || 35) / 100;
  const rows = activeCounties();
  const responseCredit = 1 - response * 0.35;
  const scenarioRows = rows.map((county) => ({
    label: county.name,
    value: county.loss * activeExposureScale() * hazard * damage * responseCredit,
  }));
  const total = scenarioRows.reduce((sum, row) => sum + row.value, 0);
  const max = Math.max(1, ...scenarioRows.map((row) => row.value));
  const chartRows = scenarioRows.map((row) => ({
    label: row.label,
    value: row.value,
    secondary: row.value,
    color: COLORS.gold,
    secondaryColor: COLORS.gold,
    valueText: `${row.value.toFixed(2)} index`,
  }));
  document.querySelector("#lossBars")?.replaceChildren(horizontalBars(chartRows, max, { rowH: 48 }));
  renderGauge(total, hazard, damage, response);
}

function renderGauge(total, hazard, damage, response) {
  const target = document.querySelector("#scenarioGauge");
  if (!target) return;
  const width = 340;
  const height = 190;
  const percent = Math.min(total / 32, 1);
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });
  svg.appendChild(
    svgEl("path", {
      d: "M 50 150 A 120 120 0 0 1 290 150",
      fill: "none",
      stroke: "#edf0ea",
      "stroke-width": 28,
      "stroke-linecap": "round",
    })
  );
  svg.appendChild(
    svgEl("path", {
      d: "M 50 150 A 120 120 0 0 1 290 150",
      fill: "none",
      stroke: COLORS.terracotta,
      "stroke-width": 28,
      "stroke-linecap": "round",
      "stroke-dasharray": `${percent * 377} 377`,
    })
  );
  svg.appendChild(svgEl("text", { x: 170, y: 124, "text-anchor": "middle", class: "bar-label" }, [
    `${total.toFixed(2)} loss index`,
  ]));
  svg.appendChild(svgEl("text", { x: 170, y: 146, "text-anchor": "middle", class: "axis-label" }, [
    `H ${(hazard * 100).toFixed(0)} / D ${(damage * 100).toFixed(0)} / R ${(response * 100).toFixed(0)}`,
  ]));
  target.replaceChildren(svg);
  const headline = document.querySelector("#scenarioHeadline");
  if (headline) {
    headline.textContent = total > 18 ? "High stress case" : total > 9 ? "Moderate stress case" : "Lower stress case";
  }
  const text = document.querySelector("#scenarioText");
  if (text) {
    text.textContent =
      "The scenario index scales the final relative loss proxy by hazard intensity, damage severity, response capacity, county selection, and facility-type exposure filter.";
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
  renderHospitalTable();
  renderSensitivityTable();
  renderScenario();
}

function render() {
  renderAll();
}

function startHazardMotion() {
  const canvas = document.querySelector("#hazardMotion");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let width = 0;
  let height = 0;
  let pixelRatio = 1;

  function resize() {
    const box = canvas.getBoundingClientRect();
    pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    width = Math.max(1, box.width);
    height = Math.max(1, box.height);
    canvas.width = Math.floor(width * pixelRatio);
    canvas.height = Math.floor(height * pixelRatio);
    ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  }

  function drawCountyField(time) {
    const sceneWidth = width < 900 ? width * 0.92 : width * 0.62;
    const sceneLeft = width < 900 ? width * 0.04 : width * 0.055;
    const sceneTop = height * 0.18;
    const sceneHeight = height * 0.66;
    const allBboxes = counties.map((county) => county.bbox);
    const minLon = Math.min(...allBboxes.map((bbox) => bbox[0]));
    const minLat = Math.min(...allBboxes.map((bbox) => bbox[1]));
    const maxLon = Math.max(...allBboxes.map((bbox) => bbox[2]));
    const maxLat = Math.max(...allBboxes.map((bbox) => bbox[3]));
    const scaleX = (lon) => sceneLeft + ((lon - minLon) / (maxLon - minLon)) * sceneWidth;
    const scaleY = (lat) => sceneTop + sceneHeight - ((lat - minLat) / (maxLat - minLat)) * sceneHeight;

    counties.forEach((county) => {
      const [minX, minY, maxX, maxY] = county.bbox;
      const x = scaleX(minX);
      const y = scaleY(maxY);
      const w = scaleX(maxX) - scaleX(minX);
      const h = scaleY(minY) - scaleY(maxY);
      const active = selectedCounty === "All" || selectedCounty === county.name;
      const shimmer = 0.08 + 0.05 * Math.sin(time * 0.0018 + county.density);
      ctx.save();
      ctx.globalAlpha = active ? 0.82 : 0.2;
      ctx.fillStyle = `rgba(231, 232, 209, ${shimmer})`;
      ctx.strokeStyle = active ? "rgba(231, 232, 209, 0.52)" : "rgba(231, 232, 209, 0.18)";
      ctx.lineWidth = active ? 1.4 : 0.8;
      ctx.beginPath();
      canvasRoundRect(ctx, x, y, w, h, 8);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    });
  }

  function draw(time) {
    ctx.clearRect(0, 0, width, height);
    const cx = width < 900 ? width * 0.52 : width * 0.34;
    const cy = height * 0.52;
    const funnelScale = width < 900 ? 0.78 : 1;
    const exposureScale = selectedBuffer / 1000;

    const glow = ctx.createRadialGradient(cx, cy, 8, cx, cy, Math.max(width, height) * 0.55);
    glow.addColorStop(0, "rgba(184, 80, 66, 0.34)");
    glow.addColorStop(0.36, "rgba(66, 106, 120, 0.2)");
    glow.addColorStop(1, "rgba(47, 41, 37, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, width, height);

    drawCountyField(time);

    for (let ring = 0; ring < 4; ring += 1) {
      const wobble = Math.sin(time * 0.0015 + ring) * 5;
      const radiusX = (88 + ring * 52 + exposureScale * 26 + wobble) * funnelScale;
      const radiusY = (28 + ring * 18 + exposureScale * 12 - wobble * 0.22) * funnelScale;
      ctx.save();
      ctx.translate(cx, cy + ring * 4);
      ctx.rotate(time * 0.00018 * (ring + 1));
      ctx.strokeStyle = ring === 0 ? "rgba(231, 232, 209, 0.54)" : "rgba(167, 190, 174, 0.26)";
      ctx.lineWidth = ring === 0 ? 2.2 : 1.2;
      ctx.setLineDash([10, 12]);
      ctx.beginPath();
      ctx.ellipse(0, 0, radiusX, radiusY, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    motionParticles.forEach((particle) => {
      const active = selectedCounty === "All" || selectedCounty === particle.county;
      const spin = particle.angle + time * 0.001 * particle.speed;
      const squeeze = 0.3 + particle.depth * 0.58;
      const radius = particle.radius * (0.72 + 0.14 * Math.sin(time * 0.0016 + particle.drift)) * funnelScale;
      const x = cx + Math.cos(spin) * radius * squeeze + Math.sin(time * 0.0009 + particle.drift) * 18;
      const y =
        cy +
        Math.sin(spin) * radius * 0.32 +
        (particle.depth - 0.52) * height * 0.5 -
        Math.cos(spin * 1.7) * 7;
      const alpha = active ? 0.26 + particle.depth * 0.56 : 0.07;
      ctx.fillStyle = particle.depth > 0.62 ? `rgba(231, 232, 209, ${alpha})` : `rgba(184, 80, 66, ${alpha})`;
      ctx.beginPath();
      ctx.arc(x, y, particle.size * (0.65 + exposureScale * 0.45), 0, Math.PI * 2);
      ctx.fill();
    });

    motionFacilities.forEach((facility) => {
      const active = selectedCounty === "All" || selectedCounty === facility.county;
      const x = width * facility.x;
      const y = height * facility.y;
      const pulse = 0.5 + 0.5 * Math.sin(time * 0.003 + facility.pulse);
      ctx.save();
      ctx.globalAlpha = active ? 1 : 0.22;
      ctx.strokeStyle = `rgba(231, 232, 209, ${0.22 + pulse * 0.28})`;
      ctx.lineWidth = 1.3;
      ctx.beginPath();
      ctx.arc(x, y, 14 + pulse * 20 * exposureScale, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = facility.county === "Lehigh" || facility.county === "Berks" ? COLORS.terracotta : COLORS.sage;
      ctx.beginPath();
      ctx.arc(x, y, 4 + pulse * 2.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });

    ctx.save();
    ctx.translate(cx, cy + height * 0.18);
    ctx.scale(1, 0.3);
    const coreGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 120 * funnelScale);
    coreGradient.addColorStop(0, "rgba(184, 80, 66, 0.45)");
    coreGradient.addColorStop(0.55, "rgba(231, 232, 209, 0.18)");
    coreGradient.addColorStop(1, "rgba(231, 232, 209, 0)");
    ctx.fillStyle = coreGradient;
    ctx.beginPath();
    ctx.arc(0, 0, 120 * funnelScale, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    if (!prefersReducedMotion) {
      window.requestAnimationFrame(draw);
    }
  }

  resize();
  window.addEventListener("resize", resize);
  window.requestAnimationFrame(draw);
}

renderControls();
updateWeightSliders();
render();
startHazardMotion();
