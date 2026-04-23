import { X } from "lucide-react";
import { themeOptions } from "@/features/astrology/constants/themes";
import { t } from "@/shared/utils/i18n";

export default function SettingsDrawer({
  dict,
  open,
  onClose,
  currentLang,
  onChangeLanguage,
  currentTheme,
  onChangeTheme,
}) {
  if (!open) {
    return null;
  }

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <aside
        className="fixed top-0 right-0 h-full w-[90vw] max-w-[360px] z-50 slide-in border-l border-amber-200/20"
        style={{
          background:
            "linear-gradient(180deg, var(--color-bg-mid), var(--color-bg-deep))",
        }}
      >
        <div className="p-5 border-b border-amber-200/15 flex items-center justify-between">
          <div>
            <div className="font-display text-amber-200 tracking-[0.2em] text-sm">
              {t(dict, "settings.title")}
            </div>
            <div className="text-amber-100/50 font-serif text-sm">
              {t(dict, "settings.subtitle")}
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn-ghost !px-2 !py-2"
            type="button"
            aria-label={t(dict, "settings.close")}
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-5 space-y-6 overflow-auto h-[calc(100%-84px)] scroll-divine">
          <section>
            <h3 className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
              {t(dict, "settings.languageTitle")}
            </h3>
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

          <section>
            <h3 className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
              {t(dict, "settings.themeTitle")}
            </h3>
            <div className="space-y-2">
              {themeOptions.map((theme) => (
                <button
                  key={theme.id}
                  type="button"
                  className={`w-full btn-ghost !justify-between ${currentTheme === theme.id ? "border-amber-300 text-amber-300" : ""}`}
                  onClick={() => onChangeTheme(theme.id)}
                >
                  <span>{t(dict, theme.key)}</span>
                </button>
              ))}
            </div>
          </section>

          <section>
            <h3 className="font-display text-[10px] tracking-[0.18em] text-amber-200/60 mb-3">
              {t(dict, "settings.miscTitle")}
            </h3>
            <div className="glass-card p-4 text-sm text-amber-100/75 font-sans">
              {t(dict, "settings.miscBody")}
            </div>
          </section>
        </div>
      </aside>
    </>
  );
}
