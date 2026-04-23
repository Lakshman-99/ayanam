"use client";

import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { createNatalChart } from "@/lib/api/charts";
import { getStoredAuth } from "@/lib/api/client";
import { t } from "@/shared/utils/i18n";

function toDms(value, positiveRef, negativeRef) {
  const abs = Math.abs(value);
  const deg = Math.floor(abs);
  const minFloat = (abs - deg) * 60;
  const min = Math.floor(minFloat);
  const sec = Math.floor((minFloat - min) * 60);
  const ref = value >= 0 ? positiveRef : negativeRef;
  return `${String(deg).padStart(2, "0")}\u00B0 ${String(min).padStart(2, "0")}' ${String(sec).padStart(2, "0")}\" ${ref}`;
}

function normalizeBirthDate(value) {
  const raw = String(value || "").trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return raw;
  }

  const match = raw.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
  if (match) {
    return `${match[3]}-${match[2]}-${match[1]}`;
  }

  return raw;
}

function normalizeBirthTime(value) {
  const raw = String(value || "").trim();
  if (/^\d{2}:\d{2}$/.test(raw)) {
    return `${raw}:00`;
  }
  if (/^\d{2}:\d{2}:\d{2}$/.test(raw)) {
    return raw;
  }
  return raw;
}

function parseCoordinate(raw) {
  const value = String(raw || "").trim();
  const numeric = Number(value);
  if (!Number.isNaN(numeric)) {
    return numeric;
  }

  const dmsMatch = value.match(
    /^(\d{1,3})\D+(\d{1,2})\D+(\d{1,2})\D*([NSEW])$/i,
  );
  if (!dmsMatch) {
    return Number.NaN;
  }

  const deg = Number(dmsMatch[1]);
  const min = Number(dmsMatch[2]);
  const sec = Number(dmsMatch[3]);
  const ref = dmsMatch[4].toUpperCase();
  const sign = ref === "S" || ref === "W" ? -1 : 1;

  return sign * (deg + min / 60 + sec / 3600);
}

export default function NewChartView({ dict, onSave }) {
  const [form, setForm] = useState({
    name: "",
    gender: "male",
    date: "",
    time: "",
    place: "",
    state: "",
    country: "",
    latitude: "",
    longitude: "",
    birthTz: "Asia/Kolkata",
  });
  const [searchText, setSearchText] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState({ type: "", message: "" });

  const canSave = useMemo(
    () =>
      form.name &&
      form.date &&
      form.time &&
      form.place &&
      form.latitude &&
      form.longitude &&
      form.birthTz,
    [form],
  );

  const update = (field, value) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  useEffect(() => {
    const text = searchText.trim();
    if (!text) {
      return undefined;
    }

    const controller = new AbortController();
    const handle = window.setTimeout(() => {
      const run = async () => {
        setLoading(true);
        try {
          const response = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(text)}&count=8&language=en&format=json`,
            { signal: controller.signal },
          );
          const payload = await response.json();
          setResults(payload.results || []);
        } catch (error) {
          if (error?.name === "AbortError") {
            return;
          }
          setResults([]);
        } finally {
          setLoading(false);
        }
      };

      run();
    }, 280);

    return () => {
      window.clearTimeout(handle);
      controller.abort();
    };
  }, [searchText]);

  const applyPlace = (item) => {
    update("place", item.name || "");
    update("state", item.admin1 || item.admin2 || "");
    update("country", item.country || "");
    update("latitude", toDms(item.latitude, "N", "S"));
    update("longitude", toDms(item.longitude, "E", "W"));
    update("birthTz", item.timezone || "Asia/Kolkata");
    setResults([]);
  };

  const save = async () => {
    if (!canSave) {
      return;
    }

    setSaving(true);
    setStatus({ type: "", message: "" });

    const birthLat = parseCoordinate(form.latitude);
    const birthLon = parseCoordinate(form.longitude);

    if (Number.isNaN(birthLat) || Number.isNaN(birthLon)) {
      setSaving(false);
      setStatus({
        type: "error",
        message: "Coordinates are invalid. Please use decimal or DMS format.",
      });
      return;
    }

    const auth = getStoredAuth();
    const birthDate = normalizeBirthDate(form.date);
    const birthTime = normalizeBirthTime(form.time);
    const birthLocationName = [form.place, form.state, form.country]
      .filter(Boolean)
      .join(", ");

    if (auth.accessToken) {
      try {
        const remoteChart = await createNatalChart({
          payload: {
            birth_name: form.name,
            birth_date: birthDate,
            birth_time: birthTime,
            birth_tz: form.birthTz,
            birth_lat: birthLat,
            birth_lon: birthLon,
            birth_location_name: birthLocationName || form.place,
            ayanamsa: "KP",
            house_system: "Placidus",
          },
          accessToken: auth.accessToken,
          tenantSlug: auth.tenantSlug,
          fallbackName: form.name,
        });

        onSave(remoteChart);
        setSaving(false);
        return;
      } catch (error) {
        setStatus({
          type: "error",
          message:
            error instanceof Error
              ? error.message
              : "Backend calculation failed. Saved locally instead.",
        });
      }
    }

    onSave({
      id: `chart_${Date.now()}`,
      refNo: String(Math.floor(Math.random() * 9000) + 1000),
      name: form.name,
      gender: form.gender,
      date: form.date,
      time: form.time,
      place: form.place,
      state: form.state,
      country: form.country,
      latitude: form.latitude,
      longitude: form.longitude,
      lagna: { sign: "--", signEn: "Unknown", deg: "--" },
      rasi: { sign: "--", signEn: "Unknown", star: "--", pada: 0 },
      currentDasha: { mahaDasha: "--", start: "--", end: "--" },
      planets: [],
    });

    if (!auth.accessToken) {
      setStatus({
        type: "info",
        message: "No login token found. Horoscope saved locally.",
      });
    }

    setSaving(false);
  };

  return (
    <div className="p-4 md:p-8 w-full max-w-[1500px] mx-auto">
      <div className="mb-8">
        <div className="font-display text-[12px] tracking-[0.3em] text-amber-200/60 mb-2">
          {t(dict, "newChart.headerTag")}
        </div>
        <h1
          className="font-display text-3xl md:text-4xl gold-text"
          style={{ fontWeight: 500 }}
        >
          {t(dict, "newChart.title")}
        </h1>
        <p className="font-sans text-amber-100/80 mt-1 text-lg">
          {t(dict, "newChart.subtitle")}
        </p>
      </div>

      <div className="glass-card p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.name")}
            </label>
            <input
              className="input-divine"
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
            />
          </div>
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.gender")}
            </label>
            <select
              className="input-divine"
              value={form.gender}
              onChange={(e) => update("gender", e.target.value)}
            >
              <option value="male">{t(dict, "newChart.genders.male")}</option>
              <option value="female">
                {t(dict, "newChart.genders.female")}
              </option>
              <option value="other">{t(dict, "newChart.genders.other")}</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.date")}
            </label>
            <input
              className="input-divine"
              value={form.date}
              onChange={(e) => update("date", e.target.value)}
              placeholder={t(dict, "newChart.placeholders.date")}
            />
          </div>
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.time")}
            </label>
            <input
              className="input-divine"
              value={form.time}
              onChange={(e) => update("time", e.target.value)}
              placeholder={t(dict, "newChart.placeholders.time")}
            />
          </div>
        </div>

        <div>
          <label className="label-divine">
            {t(dict, "newChart.fields.placeSearch")}
          </label>
          <div className="relative flex-1">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-amber-200/40"
            />
            <input
              className="input-divine pl-9"
              value={searchText}
              onChange={(e) => {
                const value = e.target.value;
                setSearchText(value);
                if (!value.trim()) {
                  setResults([]);
                  setLoading(false);
                }
              }}
              placeholder={t(dict, "newChart.placePlaceholder")}
            />
          </div>
          {loading && (
            <div className="text-amber-200/60 text-sm mt-2">
              {t(dict, "newChart.searching")}
            </div>
          )}
          {results.length > 0 && (
            <div className="mt-2 border border-amber-200/15 rounded-sm overflow-hidden">
              {results.map((item) => (
                <button
                  key={`${item.id}_${item.latitude}_${item.longitude}`}
                  type="button"
                  onClick={() => applyPlace(item)}
                  className="w-full text-left px-3 py-2 data-row"
                >
                  <div className="text-amber-100 text-base">{item.name}</div>
                  <div className="text-amber-100/70 text-sm">
                    {item.admin1 || ""} · {item.country || ""}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.place")}
            </label>
            <input
              className="input-divine"
              value={form.place}
              onChange={(e) => update("place", e.target.value)}
            />
          </div>
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.state")}
            </label>
            <input
              className="input-divine"
              value={form.state}
              onChange={(e) => update("state", e.target.value)}
            />
          </div>
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.country")}
            </label>
            <input
              className="input-divine"
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
            />
          </div>
          <div>
            <label className="label-divine">
              {t(dict, "newChart.fields.latitude")}
            </label>
            <input
              className="input-divine"
              value={form.latitude}
              onChange={(e) => update("latitude", e.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="label-divine">
              {t(dict, "newChart.fields.longitude")}
            </label>
            <input
              className="input-divine"
              value={form.longitude}
              onChange={(e) => update("longitude", e.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="label-divine">Timezone</label>
            <input
              className="input-divine"
              value={form.birthTz}
              onChange={(e) => update("birthTz", e.target.value)}
              placeholder="Asia/Kolkata"
            />
          </div>
        </div>

        {status.message && (
          <div
            className={`text-sm px-3 py-2 border ${status.type === "error" ? "text-red-300 border-red-400/40 bg-red-950/20" : "text-amber-200 border-amber-300/30 bg-amber-900/10"}`}
          >
            {status.message}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="button"
            className="btn-primary"
            onClick={save}
            disabled={!canSave || saving}
          >
            {saving ? "Calculating..." : t(dict, "newChart.actions.save")}
          </button>
        </div>
      </div>
    </div>
  );
}
