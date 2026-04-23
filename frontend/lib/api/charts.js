import { apiRequest } from "@/lib/api/client";

const SIGNS = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
];

function pad(value) {
  return String(value).padStart(2, "0");
}

function formatDate(value) {
  if (!value) {
    return "--";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`;
}

function formatTime(value) {
  if (!value) {
    return "--";
  }
  const raw = String(value).trim();
  if (/^\d{2}:\d{2}:\d{2}$/.test(raw)) {
    const [h, m] = raw.split(":");
    return `${h}:${m}`;
  }
  return raw;
}

function toDegString(longitude) {
  if (typeof longitude !== "number") {
    return "--";
  }
  const normalized = ((longitude % 30) + 30) % 30;
  const deg = Math.floor(normalized);
  const minFloat = (normalized - deg) * 60;
  const min = Math.floor(minFloat);
  const sec = Math.floor((minFloat - min) * 60);
  return `${pad(deg)}° ${pad(min)}' ${pad(sec)}\"`;
}

function signFromLongitude(longitude) {
  if (typeof longitude !== "number") {
    return "Aries";
  }
  const index = Math.floor((((longitude % 360) + 360) % 360) / 30);
  return SIGNS[index] || "Aries";
}

function findCurrentMaha(dashaPeriods = []) {
  const today = new Date().toISOString().slice(0, 10);
  return dashaPeriods.find(
    (item) =>
      item.level === 1 && item.start_date <= today && today <= item.end_date,
  );
}

function normalizePlanets(planetsObj = {}) {
  return Object.values(planetsObj).map((planet, index) => ({
    id: String(planet.name || index).toLowerCase(),
    name: planet.name || `Planet ${index + 1}`,
    sign: planet.sign || signFromLongitude(planet.longitude),
    longitude: toDegString(planet.longitude),
    house: planet.house || null,
    retrograde: Boolean(planet.is_retrograde),
    nakshatra: planet.nakshatra || "--",
    starLord: planet.star_lord || "--",
    subLord: planet.sub_lord || "--",
  }));
}

function transformNatalChart(raw, fallbackName) {
  const chartData = raw?.chart_data || {};
  const planets = normalizePlanets(chartData.planets);
  const moon = planets.find((item) => item.name === "Moon");
  const currentMaha = findCurrentMaha(chartData.dasha_periods || []);

  return {
    id: raw.id || `chart_${Date.now()}`,
    refNo:
      String(raw.id || "")
        .slice(0, 4)
        .toUpperCase() || "AUTO",
    name: raw.birth_name || fallbackName || "Unnamed",
    gender: "Other",
    date: formatDate(raw.birth_date),
    time: formatTime(raw.birth_time),
    place: raw.birth_location_name || "--",
    state: "--",
    country: "--",
    latitude:
      typeof raw.birth_lat === "number" ? raw.birth_lat.toFixed(6) : "--",
    longitude:
      typeof raw.birth_lon === "number" ? raw.birth_lon.toFixed(6) : "--",
    lagna: {
      sign: signFromLongitude(chartData.ascendant),
      signEn: signFromLongitude(chartData.ascendant),
      deg: toDegString(chartData.ascendant),
    },
    rasi: {
      sign: moon?.sign || "--",
      signEn: moon?.sign || "--",
      star: moon?.nakshatra || "--",
      pada: 0,
    },
    currentDasha: {
      mahaDasha: currentMaha?.lord || "--",
      start: formatDate(currentMaha?.start_date),
      end: formatDate(currentMaha?.end_date),
    },
    planets,
    chartData,
  };
}

export async function createNatalChart({
  payload,
  accessToken,
  tenantSlug,
  fallbackName,
}) {
  const raw = await apiRequest("/charts/natal", {
    method: "POST",
    token: accessToken,
    tenantSlug,
    body: payload,
  });

  return transformNatalChart(raw, fallbackName);
}
