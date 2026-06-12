import { writable } from 'svelte/store';

export const mapInstance = writable(null);
export const dataLoaded = writable(false);
export const activeFilter = writable(null);   // null | 'method' | 'signage'
export const activeMethod = writable(null);    // null | 'parallel' | '90' | '45'
export const activeCorridor = writable(null);  // null | 'Corridor 01' | ...
export const showAreas = writable(true);
export const showLines = writable(true);
export const lightboxStore = writable(null);
// null = all items active (no filter applied); Set = only these ids are active
export const activeLegendFilters = writable(null);
export const geojsonData = writable({ lines: null, areas: null });
export const topLotsCount = writable(20);
export const topLotsCategories = writable(new Set(['yard', 'commercial']));
export const showCurrentParking = writable(false);
export const showSensitivityZones = writable(false);
// Active lens for the merged Field Surveys step: 'occupancy' | 'paidfree'.
// Retained/removed is NOT a lens — it's the cross-cutting filter below.
export const fieldSurveyMode = writable('occupancy');
// Retained/removed filter. When true, paths removed by the BRT redesign are hidden
// from whichever lens is active (the surviving network keeps its lens colouring).
export const fieldSurveyRetained = writable(false);
// Which surveyed area the Field Surveys dashboard is reporting on. Driven by the
// viewport: 'all' when zoomed out enough to see every neighbourhood, otherwise the
// area the reader has zoomed into ('malatia' | 'garegin' | 'mega' | 'komitas' | 'shiraz').
export const fieldSurveyArea = writable('all');
// Per-area, per-mode dashboard stat blocks, loaded from field-surveys.geojson's
// `areaStats`. Shape: { all|malatia|garegin|mega|komitas|shiraz: { occupancy|paidfree|retained: [...] } }.
export const fieldSurveyStats = writable(null);
