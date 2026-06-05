import { createCanvas, loadImage } from 'canvas';
import { writeFileSync } from 'fs';

const img = await loadImage('./Parking New Design/brt_hires-1.jpg');

function crop(img, x, y, w, h, filename, scale=1) {
  const outW = Math.round(w * scale);
  const outH = Math.round(h * scale);
  const c = createCanvas(outW, outH);
  const ctx = c.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(img, x, y, w, h, 0, 0, outW, outH);
  writeFileSync(`./Parking New Design/${filename}`, c.toBuffer('image/jpeg', { quality: 0.99 }));
  console.log(`Saved ${filename}: source(${x},${y}) ${w}x${h}`);
}

// satellite_full.jpg was source(3000,6100) 900x600
// Map portion appears at approx x=400-900, y=200-590 in the 900x600 image
// → in full drawing: x=3400-3900, y=6300-6690
crop(img, 3350, 6250, 620, 450, 'sat_map_tight.jpg', 2.0);

// Zoom on project box area (lower right of satellite map)
// appears at approx x=680-900, y=350-560 in source
// → in full drawing: x=3680-3900, y=6450-6660
crop(img, 3650, 6420, 280, 250, 'sat_project_box.jpg', 4.0);

// D_cut_marker - where D section cut is in the plan
crop(img, 6100, 1650, 300, 500, 'D_cut_marker.jpg', 3.0);

// South parking strip with 4x zoom for counting
crop(img, 5000, 1855, 3000, 120, 'south_strip_count.jpg', 3.0);
