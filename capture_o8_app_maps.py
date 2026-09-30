"""Output 8 (Sep 2026, Logit C28/C60/C66/C72): print map views from the app's static build.

Needs `npm run preview` (app/, port 5173) and Python Playwright. The page bundle is
patched in flight to expose the MapLibre map as window.__map; the app source is untouched.
Then run compose_o8_app_maps.py for legends, labels and the occupancy grid.
Usage: python capture_o8_app_maps.py [view ...]
"""
import json, os, re, sys, time
from playwright.sync_api import sync_playwright
OUT = r"C:/Users/user/Yerevan-Parking/Final Presentation/SEP'26/O8 app maps/raw/"
DATA = "C:/Users/user/Yerevan-Parking/app/static/data/wgs84/"

def bounds(feats):
    xs, ys = [], []
    def walk(c):
        if isinstance(c[0], (int, float)): xs.append(c[0]); ys.append(c[1])
        else: [walk(x) for x in c]
    for f in feats:
        if f["geometry"]: walk(f["geometry"]["coordinates"])
    return [[min(xs), min(ys)], [max(xs), max(ys)]]

lines = json.load(open(DATA + "parking-lines.geojson", encoding="utf-8"))["features"]
corr = [f for f in lines if f["properties"].get("impact") == "corridor"]
def cb(tag): return bounds([f for f in corr if str(f["properties"].get("corridor", "")).endswith(tag)])
ALL = bounds(corr)
fs = json.load(open(DATA + "field-surveys.geojson", encoding="utf-8"))["features"]
AREAS = sorted({f["properties"]["area"] for f in fs})
def ab(a): return bounds([f for f in fs if f["properties"]["area"] == a])

# padding leaves room for the story card (left) and legend (right)
PAD_CARD = {"top": 40, "bottom": 40, "left": 450, "right": 290}
PAD_NONE = {"top": 50, "bottom": 50, "left": 60, "right": 60}

VIEWS = {
  "reg":      dict(step=2, bounds=ALL, pad=PAD_CARD),
  "method":   dict(step=3, bounds=ALL, pad=PAD_CARD),
  "signage":  dict(step=4, bounds=ALL, pad=PAD_CARD),
  "marking":  dict(step=5, bounds=ALL, pad=PAD_CARD),
  "loc_c1":   dict(step=6, bounds=None, tag="1", pad=PAD_NONE, offstreet=True, hide_card=True, hide_legend=True),
  "loc_c2":   dict(step=6, bounds=None, tag="2", pad=PAD_NONE, offstreet=True, hide_card=True, hide_legend=True),
  "removed":  dict(step=8, bounds=ALL, pad=PAD_CARD, switch="Current parking", removed=True, hide_legend=True),
  "areas":    dict(step=9, bounds=bounds(fs), pad=PAD_NONE, hide_card=True, hide_legend=True),
}
for a in AREAS:
    VIEWS["occ_" + a] = dict(step=9, bounds=ab(a), pad=PAD_NONE, hide_card=True, hide_legend=True, zoomcap=16.2)

def patch(route):
    r = route.fetch(); body = r.text()
    body = body.replace("return e=new q.default.Map({",
                        "return window.__map=e=new q.default.Map({preserveDrawingBuffer:true,")
    route.fulfill(response=r, body=body)

def settle(pg):
    time.sleep(1.5)
    pg.wait_for_function("window.__map.loaded() && window.__map.areTilesLoaded() && !window.__map.isMoving()", timeout=60000)
    time.sleep(1.0)

want = sys.argv[1:] or list(VIEWS)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for name in want:
        v = VIEWS[name]
        pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        pg.route(re.compile(r".*/nodes/2\..*\.js"), patch)
        pg.goto(f"http://localhost:{os.environ.get('PREVIEW_PORT', '5173')}/")
        pg.wait_for_function("window.__map && window.__map.loaded()", timeout=60000)
        pg.wait_for_selector(".loading-overlay", state="detached", timeout=60000)
        pg.evaluate(f"document.querySelector('[data-step=\"{v['step']}\"]').scrollIntoView()")
        time.sleep(4)
        for label in v.get("clicks", []):
            pg.locator(".legend-panel").get_by_text(label, exact=True).click(); time.sleep(0.8)
        # print legibility: thicker supply lines
        pg.evaluate("""() => { const m = window.__map;
          for (const id of ['parking-lines-color','parking-lines-method','parking-lines-signage',
                            'parking-lines-marking','parking-lines-location'])
            if (m.getLayer(id)) m.setPaintProperty(id, 'line-width', 5); }""")
        pg.evaluate("""() => { const m = window.__map;
          for (const l of m.getStyle().layers)
            if (/boundary|aeroway|runway/.test(l.id)) m.setLayoutProperty(l.id, 'visibility', 'none'); }""")
        if name == "areas":
            pg.evaluate("""() => { const m = window.__map;
              m.setPaintProperty('field-surveys-occupancy','line-color','#2ecc71');
              m.setLayoutProperty('field-surveys-occupancy-glow','visibility','none'); }""")
        if v.get("offstreet"):
            pg.evaluate("""() => { const m = window.__map;
              m.setPaintProperty('parking-areas-fill','fill-color','#2ecc71');
              m.setPaintProperty('parking-areas-fill','fill-opacity',0.6);
              m.setPaintProperty('parking-areas-outline','line-color','#2ecc71');
              m.setPaintProperty('parking-areas-outline','line-opacity',1);
              m.setLayoutProperty('parking-areas-fill','visibility','visible');
              m.setLayoutProperty('parking-areas-outline','visibility','visible'); }""")
            cf = ["==", ["get", "corridor"], "Corridor 0" + v["tag"]]
            pg.evaluate(f"""() => {{ const m = window.__map;
              m.setFilter('parking-lines-location', ['all', ['==', ['get','impact'], 'corridor'], {json.dumps(cf)}]);
              m.setFilter('parking-areas-fill', {json.dumps(cf)});
              m.setFilter('parking-areas-outline', {json.dumps(cf)}); }}""")
        if v.get("removed"):
            pg.evaluate("""() => { const m = window.__map;
              m.setFilter('parking-lines-color', ['==', ['get', 'impact'], 'corridor']);
              m.setLayoutProperty('parking-lines-color','visibility','visible');
              m.setPaintProperty('parking-lines-color','line-color','#EF5350');
              m.setPaintProperty('parking-lines-color','line-opacity',0.95);
              m.setPaintProperty('parking-lines-color','line-width',4);
              m.setPaintProperty('new-design-corridors','line-color','#4CAF50');
              m.setPaintProperty('new-design-corridors','line-width',6);
              m.moveLayer('new-design-corridors'); }""")
        css = ".nav-dots, .maplibregl-ctrl-top-right { display:none !important; }"
        if v.get("hide_card"): css += " .story-scroller { display:none !important; }"
        if v.get("hide_legend"): css += " .legend-panel { display:none !important; }"
        pg.add_style_tag(content=css)
        bb = v["bounds"] or cb(v["tag"])
        maxz = v.get("zoomcap", 18)
        pg.evaluate(f"window.__map.fitBounds({json.dumps(bb)}, {{padding:{json.dumps(v['pad'])}, pitch:0, bearing:0, duration:0, maxZoom:{maxz}}})")
        settle(pg)
        if name == "areas":
            cents = {a: [(ab(a)[0][0]+ab(a)[1][0])/2, (ab(a)[0][1]+ab(a)[1][1])/2] for a in AREAS}
            pts = pg.evaluate(f"Object.fromEntries(Object.entries({json.dumps(cents)}).map(([k,c])=>{{const p=window.__map.project(c);return [k,[p.x,p.y]]}}))")
            json.dump(pts, open(OUT + "areas_px.json", "w"))
        pg.screenshot(path=OUT + name + ".png")
        print(name, "ok", pg.evaluate("window.__map.getZoom().toFixed(2)"))
        pg.close()
    b.close()
