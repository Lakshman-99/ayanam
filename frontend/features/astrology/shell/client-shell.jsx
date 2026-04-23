"use client";

import { useEffect, useMemo, useState, useSyncExternalStore } from "react";
import { usePathname, useRouter } from "next/navigation";
import { navigationItems } from "@/features/astrology/constants/navigation";
import {
  defaultTheme,
  themeOptions,
} from "@/features/astrology/constants/themes";
import { chartSeed } from "@/features/astrology/data/charts";
import DashboardView from "@/features/astrology/views/dashboard-view";
import ChartsView from "@/features/astrology/views/charts-view";
import DetailView from "@/features/astrology/views/detail-view";
import NewChartView from "@/features/astrology/views/new-chart-view";
import SettingsView from "@/features/astrology/views/settings-view";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import AstroSidebar from "@/features/astrology/shell/astro-sidebar";
import ConstellationBg from "@/shared/ui/constellation-bg";
import Starfield from "@/shared/ui/starfield";
import { t } from "@/shared/utils/i18n";

const noopSubscribe = () => () => {};

export default function ClientShell({ dict, currentLang }) {
  const router = useRouter();
  const pathname = usePathname();
  const hasMounted = useSyncExternalStore(
    noopSubscribe,
    () => true,
    () => false,
  );

  const [view, setView] = useState("dashboard");
  const [charts, setCharts] = useState(chartSeed);
  const [selectedId, setSelectedId] = useState(chartSeed[0].id);
  const [query, setQuery] = useState("");
  const [sidebarDefaultOpen] = useState(() => {
    if (typeof window === "undefined") {
      return true;
    }
    return window.localStorage.getItem("ayanam.sidebarCollapsed") !== "1";
  });
  const [user] = useState(() => {
    if (typeof window === "undefined") {
      return { name: "Astro User", email: "astro@example.com" };
    }
    const raw = window.localStorage.getItem("ayanam.user");
    if (!raw) {
      return { name: "Astro User", email: "astro@example.com" };
    }
    try {
      const parsed = JSON.parse(raw);
      return {
        name: parsed.name || "Astro User",
        email: parsed.email || "astro@example.com",
      };
    } catch {
      return { name: "Astro User", email: "astro@example.com" };
    }
  });
  const [greetingMotion] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    const seen = window.sessionStorage.getItem("ayanam.greeting.seen");
    if (seen) {
      return false;
    }
    window.sessionStorage.setItem("ayanam.greeting.seen", "1");
    return true;
  });
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") {
      return defaultTheme;
    }
    const preferredTheme = window.localStorage.getItem("ayanam.theme");
    if (
      preferredTheme &&
      themeOptions.some((item) => item.id === preferredTheme)
    ) {
      return preferredTheme;
    }
    return defaultTheme;
  });

  const switchLanguage = (nextLang) => {
    window.localStorage.setItem("ayanam.lang", nextLang);
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length > 0) {
      segments[0] = nextLang;
      router.push(`/${segments.join("/")}`);
      return;
    }
    router.push(`/${nextLang}`);
  };

  useEffect(() => {
    const preferredLang = window.localStorage.getItem("ayanam.lang");
    if (preferredLang && preferredLang !== currentLang) {
      const segments = pathname.split("/").filter(Boolean);
      if (segments.length > 0) {
        segments[0] = preferredLang;
        router.replace(`/${segments.join("/")}`);
        return;
      }
      router.replace(`/${preferredLang}`);
    }
  }, [currentLang, pathname, router]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("ayanam.theme", theme);
  }, [theme]);

  const selected = useMemo(
    () => charts.find((item) => item.id === selectedId) || charts[0],
    [charts, selectedId],
  );

  const handleSaveChart = (chart) => {
    setCharts((prev) => [chart, ...prev]);
    setSelectedId(chart.id);
    setView("detail");
  };

  const logout = () => {
    window.localStorage.removeItem("ayanam.user");
    router.push(`/${currentLang}/login`);
  };

  if (!hasMounted) {
    return null;
  }

  return (
    <div className="cosmic-bg">
      <ConstellationBg />
      <Starfield />

      <SidebarProvider defaultOpen={sidebarDefaultOpen}>
        <AstroSidebar
          dict={dict}
          view={view}
          onViewChange={setView}
          user={user}
          onLogout={logout}
        />

        <SidebarInset className="h-screen relative scroll-divine overflow-auto">
          <div className="md:hidden border-b border-amber-200/10 px-3 py-2 flex items-center gap-2 overflow-x-auto sticky top-0 z-20 bg-[var(--header-bg)] backdrop-blur-md">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={`mobile_${item.id}`}
                  type="button"
                  className={`btn-ghost whitespace-nowrap ${view === item.id ? "border-amber-300 text-amber-300" : ""}`}
                  onClick={() => setView(item.id)}
                >
                  <Icon size={12} /> {t(dict, item.key)}
                </button>
              );
            })}
          </div>

          <div key={view} className="fade-in min-h-[calc(100vh-120px)]">
            {view === "dashboard" && (
              <DashboardView
                dict={dict}
                charts={charts}
                selected={selected}
                greetingMotion={greetingMotion}
                onOpenCharts={() => setView("charts")}
                onOpenDetail={() => setView("detail")}
                onSelectChart={setSelectedId}
              />
            )}

            {view === "charts" && (
              <ChartsView
                dict={dict}
                charts={charts}
                selectedId={selectedId}
                query={query}
                setQuery={setQuery}
                onSelect={(id) => {
                  setSelectedId(id);
                  setView("detail");
                }}
              />
            )}

            {view === "new" && (
              <NewChartView dict={dict} onSave={handleSaveChart} />
            )}

            {view === "detail" && <DetailView dict={dict} chart={selected} />}

            {view === "settings" && (
              <SettingsView
                dict={dict}
                currentLang={currentLang}
                onChangeLanguage={switchLanguage}
                currentTheme={theme}
                onChangeTheme={setTheme}
              />
            )}
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}
