import { ChevronRight, Star } from "lucide-react";
import { ZodiacSymbol } from "@/shared/ui/astro-symbol";
import { t, tx } from "@/shared/utils/i18n";

export default function DashboardView({
  dict,
  charts,
  selected,
  greetingMotion,
  onOpenCharts,
  onOpenDetail,
  onSelectChart,
}) {
  const genderLabel = (gender) =>
    dict.gender?.[String(gender || "").toLowerCase()] || gender;

  return (
    <div className="p-4 md:p-8 w-full max-w-[1500px] mx-auto">
      <div
        className={`mb-10 relative ${greetingMotion ? "welcome-reveal" : ""}`}
      >
        <div className="font-display text-[12px] tracking-[0.3em] text-amber-200/60 mb-2 om-mark">
          {t(dict, "dashboard.welcomeTag")}
        </div>
        <h1
          className="font-display text-4xl md:text-5xl gold-text mb-2"
          style={{ fontWeight: 500 }}
        >
          {t(dict, "dashboard.title")}
        </h1>
        <p className="font-serif text-amber-100/80 text-lg md:text-xl max-w-4xl leading-relaxed">
          {t(dict, "dashboard.subtitle")}
        </p>
        <div className="hidden md:block absolute top-0 right-0 font-serif text-amber-100/40 text-base">
          {new Date().toLocaleDateString(
            selected.country === "India" ? "en-IN" : "en-CA",
            {
              weekday: "long",
              day: "numeric",
              month: "long",
              year: "numeric",
            },
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
        <div className="glass-card corner-ornament p-5 relative">
          <div className="font-display text-[11px] tracking-[0.2em] text-amber-200/60 mb-3">
            {t(dict, "dashboard.stats.totalCharts")}
          </div>
          <div className="gold-text font-display text-4xl leading-none">
            {charts.length}
          </div>
          <div className="text-amber-100/60 font-serif text-sm mt-2">
            {t(dict, "dashboard.stats.totalChartsSub")}
          </div>
        </div>

        <div className="glass-card corner-ornament p-5 relative">
          <div className="font-display text-[11px] tracking-[0.2em] text-amber-200/60 mb-3">
            {t(dict, "dashboard.stats.activeLagna")}
          </div>
          <div className="gold-text font-display text-2xl font-tamil leading-tight">
            {selected.lagna.sign}
          </div>
          <div className="text-amber-100/60 font-serif text-sm mt-2">
            {selected.lagna.deg}
          </div>
        </div>

        <div className="glass-card corner-ornament p-5 relative">
          <div className="font-display text-[11px] tracking-[0.2em] text-amber-200/60 mb-3">
            {t(dict, "dashboard.stats.activeDasha")}
          </div>
          <div className="gold-text font-display text-lg font-tamil">
            {selected.currentDasha.mahaDasha}
          </div>
          <div className="text-amber-100/60 font-serif text-sm mt-2">
            {tx(dict, "dashboard.stats.period", {
              start: selected.currentDasha.start,
              end: selected.currentDasha.end,
            })}
          </div>
        </div>

        <div className="glass-card corner-ornament p-5 relative">
          <div className="font-display text-[11px] tracking-[0.2em] text-amber-200/60 mb-3">
            {t(dict, "dashboard.stats.selectedRef")}
          </div>
          <div className="gold-text font-display text-4xl leading-none">
            {selected.refNo}
          </div>
          <div className="text-amber-100/60 font-serif text-sm mt-2">
            {selected.name}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 glass-card corner-ornament p-6 relative">
          <div className="flex items-center justify-between mb-5">
            <div>
              <div className="font-display tracking-[0.2em] text-amber-200 text-base">
                {t(dict, "dashboard.recentTitle")}
              </div>
              <div className="font-serif text-amber-100/70 text-base">
                {t(dict, "dashboard.recentSubtitle")}
              </div>
            </div>
            <button onClick={onOpenCharts} className="btn-ghost" type="button">
              {t(dict, "common.viewAll")} <ChevronRight size={11} />
            </button>
          </div>
          <div>
            {charts.slice(0, 5).map((chart) => (
              <div
                key={chart.id}
                className="data-row py-3 px-2 flex items-center justify-between cursor-pointer"
                onClick={() => {
                  onSelectChart(chart.id);
                  onOpenDetail();
                }}
              >
                <div className="flex items-center gap-4">
                  <div className="w-9 h-9 border border-amber-200/30 flex items-center justify-center font-display text-amber-200 text-xs">
                    {chart.refNo}
                  </div>
                  <div>
                    <div className="font-serif text-amber-100 text-lg leading-tight">
                      {chart.name}
                    </div>
                    <div className="text-amber-100/70 text-sm font-sans mt-1">
                      {genderLabel(chart.gender)} · {chart.date}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-amber-100/85 text-base font-serif">
                    {chart.place}
                  </div>
                  <div className="text-amber-100/60 text-sm font-sans mt-1">
                    {chart.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card corner-ornament p-6 relative">
          <div className="font-display tracking-[0.2em] text-amber-200 text-sm mb-5">
            {t(dict, "dashboard.activeTitle")}
          </div>
          <div className="text-center py-2">
            <div className="flex justify-center mb-3">
              <ZodiacSymbol sign={selected.lagna.signEn} size={42} />
            </div>
            <div className="font-serif text-amber-100 text-2xl mb-1">
              {selected.name}
            </div>
            <div className="font-tamil text-amber-300 text-sm mb-4">
              {selected.lagna.sign} · {selected.rasi.sign}
            </div>
            <div className="divider-ornate mb-4">
              <Star size={10} className="text-amber-300" />
            </div>
            <button
              onClick={onOpenDetail}
              className="btn-primary w-full justify-center mt-5"
              type="button"
            >
              {t(dict, "common.openChart")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
