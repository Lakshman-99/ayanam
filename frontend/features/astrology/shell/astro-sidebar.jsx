"use client";

import { useEffect, useRef, useState } from "react";

import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ChevronsUpDown,
  LogOut,
  PanelLeft,
  UserRound,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { navigationItems } from "@/features/astrology/constants/navigation";
import BrandMark from "@/shared/ui/brand-mark";
import { t } from "@/shared/utils/i18n";

export default function AstroSidebar({
  dict,
  view,
  onViewChange,
  user,
  onLogout,
}) {
  const { open } = useSidebar();
  const sidebarCollapsed = !open;
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  useEffect(() => {
    window.localStorage.setItem(
      "ayanam.sidebarCollapsed",
      sidebarCollapsed ? "1" : "0",
    );
  }, [sidebarCollapsed]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const openSettingsFromMenu = () => {
    setUserMenuOpen(false);
    onViewChange("settings");
  };

  const logoutFromMenu = () => {
    setUserMenuOpen(false);
    onLogout();
  };

  return (
    <Sidebar style={{ background: "var(--sidebar-bg)" }}>
      <SidebarHeader
        className={`border-b border-amber-200/10 ${sidebarCollapsed ? "px-2 py-3" : "relative px-4 pt-5 pb-3"}`}
      >
        {sidebarCollapsed ? (
          <div className="flex flex-col items-center gap-2">
            <BrandMark size={34} />
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between pr-10">
              <div className="flex items-center gap-3">
                <BrandMark size={46} />
                <div className="font-display text-amber-200 text-base tracking-[0.16em]">
                  {t(dict, "app.brand")}
                </div>
              </div>
            </div>
          </>
        )}
      </SidebarHeader>

      <SidebarContent
        id="sidebar-navigation"
        className={`${sidebarCollapsed ? "py-2" : "py-4"} scroll-divine`}
      >
        <SidebarGroup>
          {!sidebarCollapsed && (
            <SidebarGroupLabel className="mb-3 px-5 font-display text-[12px] tracking-[0.16em] text-amber-200/70 flex items-center">
              {t(dict, "nav.section")}
            </SidebarGroupLabel>
          )}

          <SidebarMenu className={sidebarCollapsed ? "space-y-1" : ""}>
            {navigationItems.map((item) => {
              const Icon = item.icon;

              return (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    isActive={view === item.id}
                    tooltip={t(dict, item.key)}
                    onClick={() => onViewChange(item.id)}
                  >
                    <Icon size={18} />
                    {!sidebarCollapsed && <span>{t(dict, item.key)}</span>}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter
        className={`mt-auto border-t border-amber-200/10 ${sidebarCollapsed ? "p-2" : "p-3"}`}
      >
        <div
          className={`mb-2 flex ${sidebarCollapsed ? "justify-center" : "justify-end"}`}
        >
          <SidebarTrigger
            className="!static !right-auto !top-auto !h-8 !w-8 !rounded-md"
            aria-controls="sidebar-navigation"
            aria-label={
              sidebarCollapsed
                ? t(dict, "sidebar.expand")
                : t(dict, "sidebar.collapse")
            }
            title={
              sidebarCollapsed
                ? t(dict, "sidebar.expand")
                : t(dict, "sidebar.collapse")
            }
          >
            {sidebarCollapsed ? (
              <ChevronsRight size={16} />
            ) : (
              <ChevronsLeft size={16} />
            )}
          </SidebarTrigger>
        </div>

        {sidebarCollapsed ? (
          <div ref={userMenuRef} className="relative w-10 mx-auto">
            {userMenuOpen && (
              <div className="absolute bottom-full left-0 z-30 mb-2 w-[272px] glass-card p-2">
                <button
                  type="button"
                  className="btn-ghost w-full !justify-start !px-3"
                  onClick={openSettingsFromMenu}
                >
                  <PanelLeft size={14} /> {t(dict, "sidebar.settings")}
                </button>
                <button
                  type="button"
                  className="btn-ghost mt-2 w-full !justify-start !px-3"
                  onClick={logoutFromMenu}
                >
                  <LogOut size={14} /> {t(dict, "sidebar.logout")}
                </button>
              </div>
            )}

            <button
              type="button"
              className="w-10 h-10 rounded-md border border-amber-200/25 flex items-center justify-center text-amber-200 mx-auto"
              aria-haspopup="menu"
              aria-expanded={userMenuOpen}
              title={user.name}
              onClick={() => setUserMenuOpen((prev) => !prev)}
            >
              <UserRound size={15} />
            </button>
          </div>
        ) : (
          <div ref={userMenuRef} className="relative">
            {userMenuOpen && (
              <div className="absolute bottom-full left-0 z-30 mb-2 w-[272px] glass-card p-2">
                <button
                  type="button"
                  className="btn-ghost w-full !justify-start"
                  onClick={openSettingsFromMenu}
                >
                  <PanelLeft size={14} /> {t(dict, "sidebar.settings")}
                </button>
                <button
                  type="button"
                  className="btn-ghost mt-2 w-full !justify-start"
                  onClick={logoutFromMenu}
                >
                  <LogOut size={14} /> {t(dict, "sidebar.logout")}
                </button>
              </div>
            )}

            <button
              type="button"
              className="glass-card w-full p-3 text-left transition-colors hover:border-amber-200/35"
              aria-haspopup="menu"
              aria-expanded={userMenuOpen}
              onClick={() => setUserMenuOpen((prev) => !prev)}
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-md border border-amber-200/25 flex items-center justify-center text-amber-200">
                  <UserRound size={16} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm text-amber-100 font-semibold truncate">
                    {user.name}
                  </div>
                  <div className="text-xs text-amber-100/65 truncate">
                    {user.email}
                  </div>
                </div>
                <ChevronsUpDown
                  size={14}
                  className={`ml-auto shrink-0 text-amber-100/65 transition-transform ${userMenuOpen ? "rotate-180" : ""}`}
                />
              </div>
            </button>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
