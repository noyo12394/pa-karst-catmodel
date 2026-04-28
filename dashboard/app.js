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

const counties = [
  {
    name: "Lehigh",
    bbox: [-75.84, 40.402, -75.354, 40.789],
    area: 906,
    pop: 374557,
    karst: 8300,
    exposed: 58,
    facilities: { hospital: 6, school: 75, fire_ems: 38, police: 14 },
    loss: 8.7,
  },
  {
    name: "Berks",
    bbox: [-76.246, 40.197, -75.604, 40.581],
    area: 2261,
    pop: 428849,
    karst: 11250,
    exposed: 83,
    facilities: { hospital: 4, school: 97, fire_ems: 72, police: 28 },
    loss: 10.9,
  },
  {
    name: "Bucks",
    bbox: [-75.477, 40.118, -74.694, 40.609],
    area: 1597,
    pop: 646538,
    karst: 6050,
    exposed: 56,
    facilities: { hospital: 7, school: 110, fire_ems: 65, police: 35 },
    loss: 8.2,
  },
  {
    name: "Montgomery",
    bbox: [-75.694, 40.08, -75.09, 40.451],
    area: 1265,
    pop: 856553,
    karst: 7320,
    exposed: 92,
    facilities: { hospital: 9, school: 160, fire_ems: 88, police: 42 },
    loss: 12.4,
  },
  {
    name: "Chester",
    bbox: [-76.058, 39.72, -75.42, 40.262],
    area: 1944,
    pop: 545823,
    karst: 8840,
    exposed: 77,
    facilities: { hospital: 5, school: 92, fire_ems: 70, police: 30 },
    loss: 9.8,
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

const bufferShare = [
  { label: "100m", value: 86, color: COLORS.terracotta },
  { label: "250m", value: 124, color: COLORS.gold },
  { label: "500m", value: 156, color: COLORS.sage },
  { label: "outside", value: 681, color: COLORS.blue },
];

let selectedCounty = "All";
let selectedScheme = "Base";

const formatNumber = new Intl.NumberFormat("en-US");
const formatPct = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

function totalFacilities(county) {
  return Object.values(county.facilities).reduce((sum, value) => sum + value, 0);
}

function activeCounties() {
  return selectedCounty === "All"
    ? counties
    : counties.filter((county) => county.name === selectedCounty);
}

function scoreCell(cell, schemeName) {
  const [h, e, c] = schemes[schemeName];
  return Math.round(1000 * (h * cell.h + e * cell.e + c * cell.c)) / 10;
}

function svgEl(tag, attrs = {}, children = []) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attrs)) {
    el.setAttribute(key, value);
  }
  for (const child of children) {
    el.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return el;
}

function renderControls() {
  const select = document.querySelector("#countySelect");
  select.innerHTML = "";
  ["All", ...counties.map((county) => county.name)].forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name === "All" ? "All counties" : name;
    select.appendChild(option);
  });
  select.value = selectedCounty;
  select.addEventListener("change", (event) => {
    selectedCounty = event.target.value;
    render();
  });

  document.querySelectorAll(".segment").forEach((button) => {
    button.addEventListener("click", () => {
      selectedScheme = button.dataset.scheme;
      document
        .querySelectorAll(".segment")
        .forEach((segment) => segment.classList.toggle("active", segment === button));
      render();
    });
  });
}

function renderMetrics() {
  const rows = activeCounties();
  const facilities = rows.reduce((sum, county) => sum + totalFacilities(county), 0);
  const karst = rows.reduce((sum, county) => sum + county.karst, 0);
  const pop = rows.reduce((sum, county) => sum + county.pop, 0);
  document.querySelector("#metricCounties").textContent = rows.length;
  document.querySelector("#metricKarst").textContent = formatNumber.format(karst);
  document.querySelector("#metricFacilities").textContent = formatNumber.format(facilities);
  document.querySelector("#metricPopulation").textContent =
    pop >= 1000000 ? `${(pop / 1000000).toFixed(2)}M` : formatNumber.format(pop);
  document.querySelector("#selectedBadge").textContent =
    selectedCounty === "All" ? "All counties" : selectedCounty;
}

function renderMap() {
  const wrap = document.querySelector("#mapViz");
  const width = 820;
  const height = 620;
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
    svg.appendChild(
      svgEl("rect", {
        x,
        y,
        width: w,
        height: h,
        rx: 5,
        class: `county-shape ${isSelected && selectedCounty !== "All" ? "selected" : ""}`,
        opacity: isSelected ? 1 : 0.22,
      })
    );
    svg.appendChild(
      svgEl("text", {
        x: x + 8,
        y: y + 19,
        class: "map-label",
        opacity: isSelected ? 1 : 0.38,
      }, [county.name])
    );

    const cx = x + w * 0.58;
    const cy = y + h * 0.56;
    const hazardR = 10 + (county.karst / 11250) * 31;
    const exposureR = 7 + (county.exposed / 92) * 20;
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

  svg.appendChild(svgEl("text", { x: 42, y: 592, class: "axis-label" }, [
    "Circle size: mapped karst density and facilities within 500m buffer",
  ]));
  wrap.replaceChildren(svg);
}

function renderCountyBars() {
  const rows = activeCounties();
  const maxValue = Math.max(...counties.map((county) => totalFacilities(county)));
  document.querySelector("#countyBars").replaceChildren(
    horizontalBars(
      rows.map((county) => ({
        label: county.name,
        value: totalFacilities(county),
        secondary: county.exposed,
        pct: county.exposed / totalFacilities(county),
        color: COLORS.sage,
        secondaryColor: COLORS.terracotta,
        valueText: `${county.exposed}/${totalFacilities(county)} (${formatPct.format(
          county.exposed / totalFacilities(county)
        )})`,
      })),
      maxValue
    )
  );
}

function horizontalBars(rows, maxValue) {
  const width = 560;
  const rowH = 38;
  const height = 34 + rows.length * rowH;
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });
  rows.forEach((row, index) => {
    const y = 28 + index * rowH;
    const barW = (row.value / maxValue) * 320;
    const exposedW = (row.secondary / maxValue) * 320;
    svg.appendChild(svgEl("text", { x: 0, y: y + 14, class: "bar-label" }, [row.label]));
    svg.appendChild(svgEl("rect", { x: 112, y, width: 320, height: 18, rx: 4, fill: "#edf0ea" }));
    svg.appendChild(svgEl("rect", { x: 112, y, width: barW, height: 18, rx: 4, fill: row.color || COLORS.sage }));
    svg.appendChild(
      svgEl("rect", {
        x: 112,
        y,
        width: exposedW,
        height: 18,
        rx: 4,
        fill: row.secondaryColor || COLORS.terracotta,
      })
    );
    svg.appendChild(svgEl("text", { x: 446, y: y + 14, class: "bar-value" }, [
      row.valueText || `${row.secondary}/${row.value} (${formatPct.format(row.pct)})`,
    ]));
  });
  return svg;
}

function renderFacilityMix() {
  const rows = activeCounties();
  const totals = { hospital: 0, school: 0, fire_ems: 0, police: 0 };
  rows.forEach((county) => {
    Object.keys(totals).forEach((key) => {
      totals[key] += county.facilities[key];
    });
  });
  const labels = [
    ["hospital", "Hospital", COLORS.terracotta],
    ["school", "School", COLORS.sage],
    ["fire_ems", "Fire/EMS", COLORS.blue],
    ["police", "Police", COLORS.gold],
  ];
  const max = Math.max(...Object.values(totals));
  document.querySelector("#facilityMix").replaceChildren(
    horizontalBars(
      labels.map(([key, label, color]) => ({
        label,
        value: totals[key],
        secondary: totals[key],
        pct: totals[key] / Object.values(totals).reduce((sum, value) => sum + value, 0),
        color,
        secondaryColor: color,
        valueText: `${totals[key]} (${formatPct.format(
          totals[key] / Object.values(totals).reduce((sum, value) => sum + value, 0)
        )})`,
      })),
      max
    )
  );
}

function renderKhi() {
  const countyFilter = selectedCounty === "All" ? null : selectedCounty;
  const rows = muniCells
    .filter((cell) => !countyFilter || cell.county === countyFilter)
    .map((cell) => ({ ...cell, score: scoreCell(cell, selectedScheme) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 6);

  const list = document.querySelector("#khiList");
  list.innerHTML = "";
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
    list.appendChild(item);
  });
}

function renderLoss() {
  const rows = activeCounties();
  const max = Math.max(...counties.map((county) => county.loss));
  document.querySelector("#lossBars").replaceChildren(
    horizontalBars(
      rows.map((county) => ({
        label: county.name,
        value: county.loss,
        secondary: county.loss,
        pct: county.loss / max,
        color: COLORS.gold,
        secondaryColor: COLORS.gold,
        valueText: `${county.loss.toFixed(1)} index`,
      })),
      max
    )
  );
}

function renderDonut() {
  const total = bufferShare.reduce((sum, item) => sum + item.value, 0);
  const width = 310;
  const height = 260;
  const cx = 125;
  const cy = 120;
  const r = 78;
  const stroke = 28;
  const circumference = 2 * Math.PI * r;
  let offset = 0;
  const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}` });

  svg.appendChild(
    svgEl("circle", {
      cx,
      cy,
      r,
      fill: "none",
      stroke: "#edf0ea",
      "stroke-width": stroke,
    })
  );

  bufferShare.forEach((item) => {
    const length = (item.value / total) * circumference;
    const circle = svgEl("circle", {
      cx,
      cy,
      r,
      fill: "none",
      stroke: item.color,
      "stroke-width": stroke,
      "stroke-dasharray": `${length} ${circumference - length}`,
      "stroke-dashoffset": -offset,
      transform: `rotate(-90 ${cx} ${cy})`,
    });
    svg.appendChild(circle);
    offset += length;
  });

  svg.appendChild(svgEl("text", { x: cx, y: cy - 4, "text-anchor": "middle", class: "bar-label" }, [
    formatNumber.format(total),
  ]));
  svg.appendChild(svgEl("text", { x: cx, y: cy + 16, "text-anchor": "middle", class: "axis-label" }, [
    "facilities",
  ]));

  bufferShare.forEach((item, index) => {
    const y = 58 + index * 32;
    svg.appendChild(svgEl("rect", { x: 224, y: y - 12, width: 13, height: 13, rx: 3, fill: item.color }));
    svg.appendChild(svgEl("text", { x: 244, y, class: "bar-value" }, [
      `${item.label}: ${item.value}`,
    ]));
  });

  document.querySelector("#bufferDonut").replaceChildren(svg);
}

function render() {
  renderMetrics();
  renderMap();
  renderCountyBars();
  renderFacilityMix();
  renderKhi();
  renderLoss();
  renderDonut();
}

renderControls();
render();
