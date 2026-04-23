import { t, tx } from "@/shared/utils/i18n";
import {
  PlanetSymbol,
  ZodiacSymbol,
  zodiacOrder,
} from "@/shared/ui/astro-symbol";

export default function DetailView({ dict, chart }) {
  const genderLabel =
    dict.gender?.[String(chart.gender || "").toLowerCase()] || chart.gender;
  const planetsMap = chart?.chartData?.planets || {};
  const cuspList = chart?.chartData?.cusps || [];
  const dashaList = chart?.chartData?.dasha_periods || [];
  const detailedPlanets = Object.values(planetsMap);
  const topDashas = dashaList.filter((item) => item.level === 1).slice(0, 9);

  const items = [
    [t(dict, "detail.labels.name"), chart.name],
    [t(dict, "detail.labels.reference"), chart.refNo],
    [t(dict, "detail.labels.gender"), genderLabel],
    [t(dict, "detail.labels.datetime"), `${chart.date} · ${chart.time}`],
    [
      t(dict, "detail.labels.place"),
      tx(dict, "detail.placeFormat", {
        city: chart.place,
        state: chart.state,
        country: chart.country,
      }),
    ],
    [t(dict, "detail.labels.latitude"), chart.latitude || "--"],
    [t(dict, "detail.labels.longitude"), chart.longitude || "--"],
    [
      t(dict, "detail.labels.lagna"),
      `${chart.lagna.sign} (${chart.lagna.signEn}) · ${chart.lagna.deg}`,
    ],
    [
      t(dict, "detail.labels.rasi"),
      `${chart.rasi.sign} (${chart.rasi.signEn})`,
    ],
    [
      t(dict, "detail.labels.dasha"),
      `${chart.currentDasha.mahaDasha} · ${chart.currentDasha.start} → ${chart.currentDasha.end}`,
    ],
  ];

  return (
    <div className="p-4 md:p-8 w-full max-w-[1500px] mx-auto">
      <div className="mb-8">
        <div className="font-display text-[12px] tracking-[0.3em] text-amber-200/60 mb-2">
          {t(dict, "detail.headerTag")}
        </div>
        <h1
          className="font-display text-3xl md:text-4xl gold-text"
          style={{ fontWeight: 500 }}
        >
          {t(dict, "detail.title")}
        </h1>
        <p className="font-serif text-amber-100/80 mt-1 text-lg">
          {chart.name}
        </p>
      </div>

      <div className="glass-card corner-ornament p-5 relative">
        {items.map(([label, value]) => (
          <div
            key={label}
            className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 data-row py-3 px-2 items-start md:items-center"
          >
            <div className="md:col-span-4 font-display text-[11px] tracking-[0.18em] text-amber-200/60">
              {label}
            </div>
            <div className="md:col-span-8 font-serif text-amber-100 text-lg leading-relaxed">
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
        <div className="glass-card p-4">
          <div className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
            {t(dict, "detail.zodiacTitle")}
          </div>
          <div className="grid grid-cols-6 gap-2">
            {zodiacOrder.map((sign) => (
              <div
                key={sign}
                className="flex flex-col items-center gap-1 text-[10px] text-amber-100/70 font-sans"
              >
                <ZodiacSymbol sign={sign} size={30} />
                <span>{sign}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
            {t(dict, "detail.planetsTitle")}
          </div>
          <div className="space-y-2">
            {(chart.planets || []).map((planet) => (
              <div
                key={planet.id}
                className="flex items-center gap-3 px-2 py-1.5 border border-amber-200/10 rounded-sm"
              >
                <PlanetSymbol planet={planet.name} size={24} />
                <div className="text-sm text-amber-100/90 font-sans flex-1">
                  {planet.name}
                </div>
                <div className="text-xs text-amber-200/60 font-display tracking-wider">
                  {planet.sign}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 mt-5">
        <section className="glass-card p-4">
          <div className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
            NATAL PLANET CALCULATIONS
          </div>
          {detailedPlanets.length > 0 ? (
            <div className="space-y-2 max-h-[420px] overflow-auto scroll-divine pr-1">
              {detailedPlanets.map((planet) => (
                <div
                  key={planet.name}
                  className="grid grid-cols-12 gap-2 text-sm border border-amber-200/10 px-2 py-2"
                >
                  <div className="col-span-3 text-amber-100 font-serif">
                    {planet.name}
                  </div>
                  <div className="col-span-2 text-amber-100/75">
                    {planet.sign}
                  </div>
                  <div className="col-span-3 text-amber-200/80 font-display text-xs tracking-wide">
                    {planet.degree_in_sign || "--"}
                  </div>
                  <div className="col-span-2 text-amber-100/75">
                    H{planet.house || "--"}
                  </div>
                  <div className="col-span-2 text-amber-100/70 text-xs">
                    {planet.nakshatra || "--"}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-amber-100/60 text-sm">
              Detailed planet rows appear after backend natal calculation.
            </div>
          )}
        </section>

        <section className="glass-card p-4">
          <div className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
            HOUSE CUSP STRUCTURE
          </div>
          {cuspList.length > 0 ? (
            <div className="space-y-2 max-h-[420px] overflow-auto scroll-divine pr-1">
              {cuspList.map((cusp) => (
                <div
                  key={`cusp_${cusp.house}`}
                  className="grid grid-cols-12 gap-2 text-sm border border-amber-200/10 px-2 py-2"
                >
                  <div className="col-span-2 text-amber-300 font-display">
                    H{cusp.house}
                  </div>
                  <div className="col-span-3 text-amber-100/85">
                    {cusp.sign || "--"}
                  </div>
                  <div className="col-span-3 text-amber-200/80 text-xs font-display tracking-wide">
                    {cusp.degree_in_sign || "--"}
                  </div>
                  <div className="col-span-2 text-amber-100/70 text-xs">
                    {cusp.star_lord || "--"}
                  </div>
                  <div className="col-span-2 text-amber-100/70 text-xs">
                    {cusp.sub_lord || "--"}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-amber-100/60 text-sm">
              Cusp data is available after API-based natal chart generation.
            </div>
          )}
        </section>
      </div>

      <section className="glass-card p-4 mt-5">
        <div className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
          MAHADASHA TIMELINE
        </div>
        {topDashas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
            {topDashas.map((period) => {
              const isCurrent =
                period.start_date <= new Date().toISOString().slice(0, 10) &&
                new Date().toISOString().slice(0, 10) <= period.end_date;
              return (
                <div
                  key={`${period.lord}_${period.start_date}`}
                  className={`border px-3 py-2 ${isCurrent ? "border-amber-300/60 bg-amber-200/10" : "border-amber-200/10"}`}
                >
                  <div className="font-serif text-amber-100">{period.lord}</div>
                  <div className="text-xs text-amber-100/70 mt-1">
                    {period.start_date} to {period.end_date}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-amber-100/60 text-sm">
            Mahadasha sequence will render when chart_data.dasha_periods is
            present.
          </div>
        )}
      </section>
    </div>
  );
}
