import { themeOptions } from "@/features/astrology/constants/themes";
import { t } from "@/shared/utils/i18n";

export default function SettingsView({
  dict,
  currentLang,
  onChangeLanguage,
  currentTheme,
  onChangeTheme,
}) {
  const usagePercent = 38;

  return (
    <div className="p-4 md:p-8 w-full max-w-[1100px] mx-auto">
      <div className="mb-8">
        <div className="font-display text-[12px] tracking-[0.3em] text-amber-200/70 mb-2">
          {t(dict, "settings.pageTag")}
        </div>
        <h1
          className="font-display text-3xl md:text-4xl gold-text"
          style={{ fontWeight: 500 }}
        >
          {t(dict, "settings.pageTitle")}
        </h1>
        <p className="font-serif text-amber-100/80 text-lg mt-1">
          {t(dict, "settings.pageSubtitle")}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <section className="glass-card p-5">
          <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
            {t(dict, "settings.languageTitle")}
          </h2>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              className={`btn-ghost !justify-center ${currentLang === "en" ? "border-amber-300 text-amber-300" : ""}`}
              onClick={() => onChangeLanguage("en")}
            >
              {t(dict, "settings.languages.en")}
            </button>
            <button
              type="button"
              className={`btn-ghost !justify-center ${currentLang === "ta" ? "border-amber-300 text-amber-300" : ""}`}
              onClick={() => onChangeLanguage("ta")}
            >
              {t(dict, "settings.languages.ta")}
            </button>
          </div>
        </section>

        <section className="glass-card p-5">
          <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
            {t(dict, "settings.themeTitle")}
          </h2>
          <div className="space-y-2">
            {themeOptions.map((theme) => (
              <button
                key={theme.id}
                type="button"
                className={`btn-ghost w-full !justify-between ${currentTheme === theme.id ? "border-amber-300 text-amber-300" : ""}`}
                onClick={() => onChangeTheme(theme.id)}
              >
                <span>{t(dict, theme.key)}</span>
              </button>
            ))}
          </div>
        </section>
      </div>

      <section className="glass-card p-5 mt-5">
        <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
          {t(dict, "settings.miscTitle")}
        </h2>
        <p className="font-sans text-amber-100/80 text-base leading-relaxed">
          {t(dict, "settings.miscBody")}
        </p>
      </section>

      <section className="glass-card p-5 mt-5">
        <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
          {t(dict, "settings.workspaceTitle")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-3 border border-amber-200/15">
            <div className="text-amber-100/60 text-xs">
              {t(dict, "settings.workspaceName")}
            </div>
            <div className="text-amber-100 text-base mt-1">
              Ayanam Workspace
            </div>
          </div>
          <div className="p-3 border border-amber-200/15">
            <div className="text-amber-100/60 text-xs">
              {t(dict, "settings.workspacePlan")}
            </div>
            <div className="text-amber-100 text-base mt-1">Enterprise</div>
          </div>
        </div>
      </section>

      <section className="glass-card p-5 mt-5">
        <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
          {t(dict, "settings.usageTitle")}
        </h2>
        <div className="text-amber-100/80 text-sm mb-2">
          {t(dict, "settings.usageSub")}
        </div>
        <div className="bar-track">
          <div className="bar-fill" style={{ width: `${usagePercent}%` }} />
        </div>
        <div className="text-amber-100/70 text-sm mt-2">{usagePercent}%</div>
      </section>

      <section className="glass-card p-5 mt-5">
        <h2 className="font-display text-[11px] tracking-[0.2em] text-amber-200/70 mb-3">
          {t(dict, "settings.teamTitle")}
        </h2>
        <div className="space-y-2">
          {["admin@ayanam.ai", "astro1@ayanam.ai", "astro2@ayanam.ai"].map(
            (email) => (
              <div
                key={email}
                className="data-row py-2 px-1 flex items-center justify-between"
              >
                <span className="text-amber-100 text-sm">{email}</span>
                <span className="text-amber-100/60 text-xs">
                  {t(dict, "settings.teamRole")}
                </span>
              </div>
            ),
          )}
        </div>
      </section>

      <section className="glass-card p-5 mt-5 border-red-400/30">
        <h2 className="font-display text-[11px] tracking-[0.2em] text-red-300 mb-3">
          {t(dict, "settings.dangerTitle")}
        </h2>
        <p className="font-sans text-amber-100/75 text-sm leading-relaxed mb-3">
          {t(dict, "settings.dangerBody")}
        </p>
        <button
          type="button"
          className="btn-ghost !text-red-300 !border-red-300/40"
        >
          {t(dict, "settings.dangerAction")}
        </button>
      </section>
    </div>
  );
}
