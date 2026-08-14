// src/components/ds/dsAttr.ts
//
// Every design-system component must carry `data-ds` so the defaults in
// design-system.css apply to it: with Tailwind Preflight disabled, the
// `[data-ds]` rules supply border-box sizing and the soft default border
// colour, so Tailwind `border` / `border-ds-*` utilities work normally.
//
// Spread onto the rendered root element:  <button {...dsRoot} … />
export const dsRoot = { 'data-ds': '' } as const;
