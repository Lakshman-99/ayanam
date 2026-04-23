import { Search, ChevronRight } from "lucide-react";
import { t, tx } from "@/shared/utils/i18n";

export default function ChartsView({
  dict,
  charts,
  selectedId,
  query,
  setQuery,
  onSelect,
}) {
  const genderLabel = (gender) =>
    dict.gender?.[String(gender || "").toLowerCase()] || gender;

  const filtered = charts.filter((chart) => {
    const q = query.toLowerCase();
    return chart.name.toLowerCase().includes(q) || chart.refNo.includes(q);
  });

  return (
    <div className="p-4 md:p-8 w-full max-w-[1500px] mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <div className="font-display text-[12px] tracking-[0.3em] text-amber-200/60 mb-2">
            {t(dict, "charts.headerTag")}
          </div>
          <h1
            className="font-display text-3xl md:text-4xl gold-text"
            style={{ fontWeight: 500 }}
          >
            {t(dict, "charts.title")}
          </h1>
          <p className="font-serif text-amber-100/80 mt-1 text-lg">
            {tx(dict, "charts.subtitle", { count: charts.length })}
          </p>
        </div>

        <div className="relative">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-amber-200/40"
          />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="input-divine pl-9 w-full md:w-96"
            placeholder={t(dict, "charts.searchPlaceholder")}
          />
        </div>
      </div>

      <div className="glass-card corner-ornament relative overflow-x-auto">
        <div className="min-w-[920px]">
          <div className="grid grid-cols-12 px-5 py-3 border-b border-amber-200/15 text-[11px] font-display tracking-[0.18em] text-amber-200/70">
            <div className="col-span-1">{t(dict, "charts.columns.ref")}</div>
            <div className="col-span-3">{t(dict, "charts.columns.name")}</div>
            <div className="col-span-1">{t(dict, "charts.columns.gender")}</div>
            <div className="col-span-2">
              {t(dict, "charts.columns.birthDate")}
            </div>
            <div className="col-span-2">{t(dict, "charts.columns.time")}</div>
            <div className="col-span-2">{t(dict, "charts.columns.place")}</div>
            <div className="col-span-1 text-right">
              {t(dict, "charts.columns.action")}
            </div>
          </div>

          {filtered.map((chart) => (
            <div
              key={chart.id}
              className={`grid grid-cols-12 px-5 py-4 data-row cursor-pointer ${chart.id === selectedId ? "selected" : ""}`}
              onClick={() => onSelect(chart.id)}
            >
              <div className="col-span-1 font-display text-amber-300/80 text-sm">
                {chart.refNo}
              </div>
              <div className="col-span-3 font-serif text-amber-100 text-lg leading-tight">
                {chart.name}
              </div>
              <div className="col-span-1 font-sans text-amber-100/75 text-sm uppercase tracking-wider">
                {genderLabel(chart.gender)}
              </div>
              <div className="col-span-2 font-sans text-amber-100/80 text-sm">
                {chart.date}
              </div>
              <div className="col-span-2 font-sans text-amber-100/80 text-sm">
                {chart.time}
              </div>
              <div className="col-span-2 font-serif text-amber-100/85 text-base">
                {chart.place}
              </div>
              <div className="col-span-1 text-right">
                <ChevronRight size={14} className="text-amber-300 inline" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
