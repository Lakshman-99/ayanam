"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { PanelLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const SidebarContext = React.createContext(null);

export function useSidebar() {
  const context = React.useContext(SidebarContext);

  if (!context) {
    throw new Error("useSidebar must be used within SidebarProvider.");
  }

  return context;
}

export function SidebarProvider({
  defaultOpen = true,
  open: openProp,
  onOpenChange,
  className,
  children,
}) {
  const [openState, setOpenState] = React.useState(defaultOpen);
  const open = openProp ?? openState;

  const setOpen = React.useCallback(
    (value) => {
      if (onOpenChange) {
        const nextOpen = typeof value === "function" ? value(open) : value;
        onOpenChange(nextOpen);
        return;
      }

      setOpenState((prevOpen) =>
        typeof value === "function" ? value(prevOpen) : value,
      );
    },
    [onOpenChange, open],
  );

  const toggleSidebar = React.useCallback(() => {
    setOpen((prevOpen) => !prevOpen);
  }, [setOpen]);

  const contextValue = React.useMemo(
    () => ({ open, setOpen, toggleSidebar }),
    [open, setOpen, toggleSidebar],
  );

  return (
    <SidebarContext.Provider value={contextValue}>
      <div
        className={cn(
          "group/sidebar-wrapper flex min-h-screen w-full",
          className,
        )}
        data-state={open ? "expanded" : "collapsed"}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  );
}

export const Sidebar = React.forwardRef(function Sidebar(
  { className, ...props },
  ref,
) {
  const { open } = useSidebar();

  return (
    <aside
      ref={ref}
      data-state={open ? "expanded" : "collapsed"}
      className={cn(
        "hidden md:flex flex-col border-r border-amber-200/10 h-screen sticky top-0 transition-[width] duration-200 z-20",
        open ? "w-[304px]" : "w-[68px]",
        className,
      )}
      {...props}
    />
  );
});

export const SidebarInset = React.forwardRef(function SidebarInset(
  { className, ...props },
  ref,
) {
  return (
    <main ref={ref} className={cn("min-w-0 flex-1", className)} {...props} />
  );
});

export const SidebarHeader = React.forwardRef(function SidebarHeader(
  { className, ...props },
  ref,
) {
  return <div ref={ref} className={cn(className)} {...props} />;
});

export const SidebarContent = React.forwardRef(function SidebarContent(
  { className, ...props },
  ref,
) {
  return (
    <div
      ref={ref}
      className={cn("flex-1 overflow-y-auto", className)}
      {...props}
    />
  );
});

export const SidebarFooter = React.forwardRef(function SidebarFooter(
  { className, ...props },
  ref,
) {
  return <div ref={ref} className={cn(className)} {...props} />;
});

export const SidebarGroup = React.forwardRef(function SidebarGroup(
  { className, ...props },
  ref,
) {
  return <div ref={ref} className={cn(className)} {...props} />;
});

export const SidebarGroupLabel = React.forwardRef(function SidebarGroupLabel(
  { className, ...props },
  ref,
) {
  return <div ref={ref} className={cn(className)} {...props} />;
});

export const SidebarMenu = React.forwardRef(function SidebarMenu(
  { className, ...props },
  ref,
) {
  return (
    <ul ref={ref} className={cn("m-0 list-none p-0", className)} {...props} />
  );
});

export const SidebarMenuItem = React.forwardRef(function SidebarMenuItem(
  { className, ...props },
  ref,
) {
  return <li ref={ref} className={cn(className)} {...props} />;
});

const sidebarMenuButtonVariants = cva("nav-item nav-item-xl w-full text-left", {
  variants: {
    collapsed: {
      true: "sidebar-menu-button-collapsed h-11 w-11 mx-auto my-1 rounded-xl border border-transparent !justify-center !px-0 !gap-0",
      false: "",
    },
  },
  defaultVariants: {
    collapsed: false,
  },
});

export const SidebarMenuButton = React.forwardRef(function SidebarMenuButton(
  { asChild = false, isActive = false, tooltip, className, title, ...props },
  ref,
) {
  const { open } = useSidebar();
  const Comp = asChild ? Slot : "button";
  const isCollapsed = !open;

  return (
    <Comp
      ref={ref}
      type={asChild ? undefined : "button"}
      title={!open && tooltip ? tooltip : title}
      data-active={isActive ? "true" : "false"}
      className={cn(
        sidebarMenuButtonVariants({
          collapsed: isCollapsed,
        }),
        isActive
          ? isCollapsed
            ? "sidebar-menu-button-collapsed-active"
            : "active"
          : "",
        className,
      )}
      {...props}
    />
  );
});

export const SidebarTrigger = React.forwardRef(function SidebarTrigger(
  { className, onClick, children, ...props },
  ref,
) {
  const { open, toggleSidebar } = useSidebar();

  return (
    <button
      ref={ref}
      type="button"
      className={cn("sidebar-toggle", className)}
      aria-expanded={open}
      onClick={(event) => {
        onClick?.(event);
        if (!event.defaultPrevented) {
          toggleSidebar();
        }
      }}
      {...props}
    >
      {children ?? <PanelLeft size={16} />}
    </button>
  );
});
