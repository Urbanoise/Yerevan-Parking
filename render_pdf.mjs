import { createCanvas, loadImage } from 'canvas';
import * as pdfjsLib from './node_modules/pdfjs-dist/legacy/build/pdf.mjs';
import { readFileSync, writeFileSync } from 'fs';

function patchContext(ctx) {
  const origDrawImage = ctx.drawImage.bind(ctx);
  ctx.drawImage = async function(src, ...args) {
    try {
      return origDrawImage(src, ...args);
    } catch(e) {
      // src is pdfjs CanvasElement; src.ctx is CanvasRenderingContext2D; src.ctx.canvas is node-canvas Canvas
      const backingCanvas = src?.ctx?.canvas;
      if (backingCanvas?.toBuffer) {
        try {
          // Convert backing canvas to Image so drawImage accepts it
          const imgBuf = backingCanvas.toBuffer('image/png');
          const img = await loadImage(imgBuf);
          return origDrawImage(img, ...args);
        } catch(e2) {
          console.warn('fallback also failed:', e2.message);
        }
      }
    }
  };
  return ctx;
}

class NodeCanvasFactory {
  create(width, height) {
    const canvas = createCanvas(width, height);
    const context = patchContext(canvas.getContext('2d'));
    return { canvas, context };
  }
  reset(c, w, h) { c.canvas.width = w; c.canvas.height = h; }
  destroy(c) { c.canvas.width = 0; c.canvas.height = 0; }
}

const pdfPath = './Parking New Design/YEREVAN BRT_C1-17.04.2026_-DE-ARM.YVN.C1.00-CPD-002.pdf';
const data = new Uint8Array(readFileSync(pdfPath));
const canvasFactory = new NodeCanvasFactory();
const pdf = await pdfjsLib.getDocument({ data, canvasFactory }).promise;

const page = await pdf.getPage(1);
const viewport = page.getViewport({ scale: 2.0 });
console.log(`Canvas: ${Math.round(viewport.width)} x ${Math.round(viewport.height)}`);

const { canvas, context } = canvasFactory.create(Math.round(viewport.width), Math.round(viewport.height));
await page.render({ canvasContext: context, viewport, canvasFactory }).promise;

const buf = canvas.toBuffer('image/jpeg', { quality: 0.92 });
writeFileSync('./Parking New Design/brt_full.jpg', buf);
console.log('Saved', (buf.length/1024/1024).toFixed(2), 'MB');
