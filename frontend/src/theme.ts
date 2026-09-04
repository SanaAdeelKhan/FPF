/**
 * Central color palette — single source of truth. Every color used in the app
 * should trace back to a value here. If you're changing a color, change it here
 * once, not in scattered CSS.
 *
 * These same hex values are mirrored as CSS custom properties in theme.css
 * (CSS can't import a .ts file directly) — if you add or change a color here,
 * update theme.css to match. Exported so any component that needs a color in
 * JS (charts, dynamic inline styles) pulls from the same source instead of
 * hardcoding a hex value.
 *
 * Palette: modern professional — slate neutrals + a confident blue accent.
 * Blue reads as trustworthy/enterprise without tipping into generic SaaS —
 * paired with the serif display type, it stays distinct from a template feel.
 */

export const colors = {
  // Surfaces
  bg: "#F8FAFC",
  surface: "#FFFFFF",

  // Text
  ink: "#0F172A",
  inkSoft: "#475569",

  // Primary accent (buttons, links, active states)
  primary: "#2563EB",
  primaryDark: "#1D4ED8",
  primarySoft: "#EFF6FF",

  // Status
  success: "#059669",
  successBg: "#ECFDF5",
  danger: "#DC2626",
  dangerBg: "#FEF2F2",

  // Structure
  border: "#E2E8F0",

  // "Hidden requirements" seal — dark slate, deliberately distinct from the
  // light surfaces so a sealed section is unmistakable at a glance.
  seal: "#0F172A",
  sealStripe: "#1E293B",
} as const;

export type ColorToken = keyof typeof colors;
