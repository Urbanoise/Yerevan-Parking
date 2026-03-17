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
