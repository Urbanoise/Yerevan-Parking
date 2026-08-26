# -*- coding: utf-8 -*-
"""Canonical figure set for the Output 8 / Output 10 report revisions.

Every number the two reports quote is derived here, from the same GeoJSON the web
app serves (CLAUDE.md: the GeoJSON is the single source of truth), so the reports,
the dashboard and the ADB deck cannot drift apart.

SCOPE — this module reproduces the "C1+C2 v2" basis that the app and
"Parking Slides - 23072026.pptx" already use, and asserts against the figure set
documented in apply_slides_23072026.py:52-67. Two exclusions sit behind it:

  * Corridor 03 is withheld pending its conceptual design (HIDDEN_CORRIDORS in
    app/src/lib/config/story.js). 896 on-corridor spaces.
  * Nalbandyan016 (14 Zone A spaces) is tagged impact=corridor but lies wholly
    outside every corridor boundary polygon, so it carries corridor=None and drops
    out of the C1/C2 filter automatically.
  * Off-street drops the withdrawn NalbandyanPavstocByuzand facility (16 spaces).

With all three restored the totals are the 7,005 / 15,897 quoted in the June drafts.

Three groups of figures:
  supply()     — corridor-wide inventory and design impact (GeoJSON, C1+C2)
  survey()     — the six-area field occupancy survey (field-surveys.geojson)
  vehicles()   — vehicle-level typology from the six occupancy workbooks. This is
                 the only group that needs the raw XLSX: the observed parking
                 method, kerb location, vehicle type and legality are recorded per
                 vehicle-sighting and are not carried into the GeoJSON.
"""
import json
import os
import re
from collections import Counter, defaultdict
from functools import lru_cache

ROOT = "C:/Users/user/Yerevan-Parking"
WGS = os.path.join(ROOT, "app/static/data/wgs84")
LINES = os.path.join(WGS, "parking-lines.geojson")
AREAS = os.path.join(WGS, "parking-areas.geojson")
SURVEYS = os.path.join(WGS, "field-surveys.geojson")

CORRIDORS = ("Corridor 01", "Corridor 02")
OFFSTREET_WITHDRAWN = {"NalbandyanPavstocByuzand"}

# Design lengths, from the conceptual design rather than from the parking data.
CORRIDOR_KM = {"Corridor 01": 11.66, "Corridor 02": 19.19}

# Retention per corridor, from the v2 conceptual design (Retention Numbers.xlsx).
# The existing base is derived, not typed, so the removal line cannot drift out of
# step with the inventory the way the 22 Jul deck's did.
RETAINED = {"Corridor 01": 869, "Corridor 02": 351}

# Source-data spelling variants. The surveyors' segment names carry a handful of
# typos; folding them in is what lets the per-street tables sum exactly to their
# corridor totals instead of being "illustrative".
STREET_ALIASES = {
    "Arshaunyac": "Arshakunyac",
    "TIgranMec": "TigranMec",
    "Rafi": "Raffi",
    "Komktas": "Komitas",
    "Koimtas": "Komitas",
    "GirgorHasratyan": "GrigorHasratyan",
    "DvaitAnhaght": "DavitAnhaght",
    "kievyan": "Kievyan",
}

# Display names for the street tables (segment stem -> report label).
STREET_LABELS = {
    "Arshakunyac": "Arshakunyats Avenue",
    "Arshakunyac1st": "Arshakunyats 1st",
    "Bagratunyac": "Bagratunyats",
    "Nalbandyan": "Nalbandyan",
    "GareginNzhdeh": "Garegin Nzhdeh",
    "Abovyan": "Abovyan",
    "Amiryan": "Amiryan",
    "TigranMec": "Tigran Mets",
    "Moskovyan": "Moskovyan",
    "Agatangeghosi": "Agatangeghos",
    "Raffi": "Raffi",
    "Rubinyan": "Rubinyan",
    "Komitas": "Komitas Avenue",
    "Sebastia": "Sebastia",
    "QrqQrqoryan": "Qrq Qrqoryan",
    "DavitAnhaght": "Davit Anhaght",
    "GrigorHasratyan": "Grigor Hasratyan",
    "Kievyan": "Kievyan",
    "Kievyan1st": "Kievyan 1st",
    "Shiraz": "Shiraz",
    "Gai": "Gai",
    "VazgenACity": "Vazgen Sargsyan (City)",
    "VazgenAMherMkrtchyanSquare": "Vazgen Sargsyan / Mher Mkrtchyan Sq.",
    "Vagharshyan": "Vagharshyan",
    "Barekamutyun": "Barekamutyun",
}

# The six surveyed areas: dashboard key -> (report label, survey date, weekday,
# zone-code range). Dates from the survey campaign log quoted in Output 8 §3.1.
# Zone codes are NOT listed here — they are derived from the survey features in
# survey(), because hand-written ranges drift from the data (an earlier draft of this
# table had three of the six wrong).
SURVEY_AREAS = [
    ("kentron",  "Kentron (Corridor 1 core)",  "3 June 2026",  "Wednesday"),
    ("komitas",  "Komitas Avenue",             "29 May 2026",  "Friday"),
    ("mega",     "Gai Avenue (Mega Mall)",     "2 June 2026",  "Tuesday"),
    ("garegin",  "Garegin Nzhdeh",             "2 June 2026",  "Tuesday"),
    ("shiraz",   "Shiraz / Hasratyan",         "1 June 2026",  "Monday"),
    ("malatia",  "Malatia-Sebastia",           "3 June 2026",  "Wednesday"),
]

# Off-street facility surveyed in each area (label, formal spaces) — the Output 8
# Table 10 block; occupancy is read live from field-survey-yards.geojson metrics
# already embedded in the report, so only the labels live here.
SURVEY_YARDS = {
    "kentron": "Nalbandyan yard",
    "komitas": "Komitas City lot",
    "garegin": "GN off-street",
    "mega": "Palace lot",
    "malatia": "Sebastia yard",
    "shiraz": "Shiraz off-street",
}

WORKBOOKS = {
    "malatia": "Field Surveys/Malatia Sebastia - Analysis (corrected 24082026).xlsx",
    "kentron": "Field Surveys/Kentron - Analysis (corrected 24082026).xlsx",
    "garegin": "Field Surveys/Garegin Nzhdeh St - Analysis (corrected 24082026).xlsx",
    "mega": "Field Surveys/Gai Avenue - Analysis (corrected 24082026).xlsx",
    "komitas": "Field Surveys/Komitas - Analysis (corrected 24082026).xlsx",
    "shiraz": "Field Surveys/Shiraz, Hasratyan - Analysis (corrected 24082026).xlsx",
}
# Off-street log label per workbook (rows whose Zone is this string are the yard).
OFF_LABEL = {
    "malatia": "off-street", "kentron": "off-street", "garegin": "off-street",
    "mega": "p", "komitas": "off street city", "shiraz": "shiraz off-street",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _spaces(feature):
    try:
        return int(feature["properties"].get("space"))
    except (TypeError, ValueError):
        return 0


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["features"]


def pct(part, whole, digits=1):
    return round(100.0 * part / whole, digits) if whole else 0.0


def _street_stem(name):
    stem = re.sub(r"\d+$", "", name or "").strip()
    return STREET_ALIASES.get(stem, stem)


# ---------------------------------------------------------------------------
# supply + design impact
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def supply():
    lines, areas = _load(LINES), _load(AREAS)

    def in_scope(f):
        return f["properties"].get("corridor") in CORRIDORS

    on_corridor = [f for f in lines if in_scope(f) and f["properties"].get("impact") == "corridor"]
    cross_street = [f for f in lines if in_scope(f) and f["properties"].get("impact") == "buffer"]
    on_street = on_corridor + cross_street
    off_street = [f for f in areas
                  if in_scope(f) and f["properties"].get("name") not in OFFSTREET_WITHDRAWN]

    oc_spaces = sum(map(_spaces, on_corridor))
    d = {
        "on_corridor": oc_spaces,
        "on_corridor_segments": len(on_corridor),
        "cross_street": sum(map(_spaces, cross_street)),
        "cross_street_segments": len(cross_street),
        "on_street": sum(map(_spaces, on_street)),
        "on_street_segments": len(on_street),
        "off_street": sum(map(_spaces, off_street)),
        "off_street_facilities": len(off_street),
    }
    d["total"] = d["on_street"] + d["off_street"]
    d["features"] = d["on_street_segments"] + d["off_street_facilities"]

    # How much of the off-street stock is gated residential courtyard rather than a
    # named commercial or institutional facility — the fact that makes the absorptive
    # capacity conditional on the courtyards being opened.
    #
    # Report BOTH units. The courtyards are 92% of the FACILITIES but 83% of the
    # CAPACITY, because the 22 named lots are individually about twice the size of a
    # courtyard (mean 51 spaces against 26). The June reports and the July ADB deck
    # quote the 92%, correctly derived, but describe it as a share of capacity — which
    # is the 83% figure. Both are stated so neither reading can mislead.
    yards = [f for f in off_street
             if "yard" in (f["properties"].get("name") or "").lower()]
    d["off_street_yards"] = sum(map(_spaces, yards))
    d["off_street_yards_pct"] = pct(d["off_street_yards"], d["off_street"])
    d["off_street_named"] = d["off_street"] - d["off_street_yards"]
    d["off_street_yard_facilities"] = len(yards)
    d["off_street_named_facilities"] = d["off_street_facilities"] - len(yards)
    d["off_street_yard_facilities_pct"] = pct(len(yards), d["off_street_facilities"])

    # per-corridor: existing on-corridor supply, retained, removed
    d["corridors"] = {}
    for cor in CORRIDORS:
        existing = sum(_spaces(f) for f in on_corridor if f["properties"]["corridor"] == cor)
        retained = RETAINED[cor]
        d["corridors"][cor] = {
            "km": CORRIDOR_KM[cor],
            "existing": existing,
            "retained": retained,
            "removed": existing - retained,
            "cross_street": sum(_spaces(f) for f in cross_street
                                if f["properties"]["corridor"] == cor),
            "off_street": sum(_spaces(f) for f in off_street
                              if f["properties"]["corridor"] == cor),
            "off_street_facilities": sum(1 for f in off_street
                                         if f["properties"]["corridor"] == cor),
        }
    d["retained"] = sum(c["retained"] for c in d["corridors"].values())
    d["removed"] = sum(c["removed"] for c in d["corridors"].values())
    d["removed_pct"] = pct(d["removed"], oc_spaces, 0)
    d["retained_pct"] = pct(d["retained"], oc_spaces, 0)

    # on-corridor splits, all against the 6,095 denominator
    def split(key, mapping=None):
        c = Counter()
        for f in on_corridor:
            v = f["properties"].get(key)
            c[mapping.get(v, v) if mapping else v] += _spaces(f)
        return dict(c)

    d["zones"] = split("administration", {
        "zone a (red lines)": "zone_a", "zone b (blue lines)": "zone_b",
        "taxi": "taxi", "free": "free",
    })
    # Edge cases are folded exactly as the app's dashboard folds them
    # (StoryStep.svelte:95-101), so the report, the charts and the live dashboard
    # cannot disagree: one "mix" segment (13 spaces) counts as parallel, and the
    # same segment's missing location counts as on-street.
    d["methods"] = split("method", {"mix": "parallel", None: "parallel", "45": "45"})
    d["locations"] = split("location", {None: "on-street"})
    signage = split("signage")
    marking = split("marking")
    d["signage_yes"] = signage.get("yes", 0)
    d["signage_no"] = oc_spaces - d["signage_yes"]
    d["marking_yes"] = marking.get("yes", 0)
    d["marking_no"] = oc_spaces - d["marking_yes"]

    # Zone A concentration by street (the deck's "Nalbandyan 69, Abovyan 46 …")
    zone_a = Counter()
    for f in on_corridor:
        if f["properties"].get("administration") == "zone a (red lines)":
            zone_a[STREET_LABELS.get(_street_stem(f["properties"].get("name")),
                                     _street_stem(f["properties"].get("name")))] += _spaces(f)
    d["zone_a_streets"] = zone_a.most_common()

    # per-street tables, complete (they sum exactly to the corridor total)
    d["streets"] = {}
    for cor in CORRIDORS:
        agg = defaultdict(lambda: {"segments": 0, "spaces": 0, "parallel": 0, "perpendicular": 0})
        for f in on_corridor:
            if f["properties"]["corridor"] != cor:
                continue
            row = agg[_street_stem(f["properties"].get("name"))]
            row["segments"] += 1
            row["spaces"] += _spaces(f)
            if f["properties"].get("method") == "parallel":
                row["parallel"] += _spaces(f)
            elif f["properties"].get("method") == "90":
                row["perpendicular"] += _spaces(f)
        rows = [dict(street=STREET_LABELS.get(k, k), **v) for k, v in agg.items()]
        d["streets"][cor] = sorted(rows, key=lambda r: -r["spaces"])
        assert sum(r["spaces"] for r in rows) == d["corridors"][cor]["existing"], cor

    _assert_supply(d)
    return d


def _assert_supply(d):
    """The figure set apply_slides_23072026.py:65-67 asserts, plus the splits it
    never stated. A mismatch here means the GeoJSON moved and both reports need
    re-cutting, not that this module should be relaxed."""
    assert (d["on_corridor"], d["on_corridor_segments"]) == (6095, 433), d["on_corridor"]
    assert (d["on_street"], d["on_street_segments"]) == (7825, 606), d["on_street"]
    assert (d["off_street"], d["off_street_facilities"]) == (6732, 239), d["off_street"]
    assert d["total"] == 14557, d["total"]
    assert (d["removed"], d["retained"]) == (4875, 1220), (d["removed"], d["retained"])
    assert d["cross_street"] == d["on_street"] - d["on_corridor"] == 1730
    z = d["zones"]
    assert z["free"] + z["zone_b"] + z["zone_a"] + z["taxi"] == d["on_corridor"]
    assert (z["zone_a"], z["zone_b"], z["taxi"], z["free"]) == (246, 534, 67, 5248), z
    assert sum(d["methods"].values()) == sum(d["locations"].values()) == d["on_corridor"]
    # the folded buckets must match what the dashboard shows on steps 3 and 6
    assert d["methods"] == {"parallel": 4655, "90": 1440}, d["methods"]
    assert d["locations"] == {"on-street": 4394, "pocket": 1431, "set-back": 270}, d["locations"]
    assert sum(c["existing"] for c in d["corridors"].values()) == d["on_corridor"]


# ---------------------------------------------------------------------------
# field occupancy survey
# ---------------------------------------------------------------------------
def _turnover(feats, road_edge_only=False):
    """Vehicles per marked space per day for one area: parking events over capacity.

    Paths that recorded no events are skipped entirely rather than contributing their
    capacity to the denominator — counting them deflates every area.

    `road_edge_only` reproduces the original derivation in
    gen_field_survey_report.py:762-771, which filtered to `location == "on-street"`.
    That filter is what produced the "5-11 vehicles per space per day" quoted in the
    June reports and the July ADB deck, and it reproduces exactly (3.1 Shiraz, 5.2
    Garegin, 5.7 Komitas, 6.1 Kentron, 10.5 Gai, 11.5 Malatia) on every revision of
    the source data. It is NOT used for the headline, because its two extreme values
    rest on denominators too small to carry a number: Gai Avenue has 6 road-edge
    spaces and Malatia-Sebastia has 4, essentially all of their parking being in
    pockets and setbacks. The 11 in "5-11" is therefore a 4-space sample.

    The default counts every bay type, so the smallest denominator across the six
    areas is 132 spaces and the range (3.5-7.5) is one every area can support.
    """
    events = space = 0
    for p in feats:
        if road_edge_only and p.get("location") != "on-street":
            continue
        if p.get("parking_events") is None or not p.get("space"):
            continue
        events += p["parking_events"]
        space += p["space"]
    return round(events / space, 1) if space else 0.0


def _peak_hour(vap, capacity):
    """Area-wide occupancy at the single busiest clock hour.

    `vap` is the hourly curve of distinct vehicles observed; its maximum is the number
    that used the area's kerb during its busiest clock hour. It is the same kind of
    count as the zone-level figure - vehicles that used the kerb during the hour, not a
    snapshot of simultaneous presence - taken at one hour shared across the area rather
    than at each zone's own peak. It therefore is NOT bounded by 100%; that no area
    exceeds it in this survey is a result, not a property of the measure. Returns the
    share, the count and the hour it falls in.
    """
    if not vap or not capacity:
        return {"peak_hour_pct": None, "peak_hour": None, "peak_hour_cars": None}
    hour, cars = max(vap, key=lambda p: p[1])
    return {"peak_hour_pct": round(100.0 * cars / capacity),
            "peak_hour": hour, "peak_hour_cars": cars}


@lru_cache(maxsize=1)
def survey():
    with open(SURVEYS, encoding="utf-8") as fh:
        doc = json.load(fh)
    stats, disp = doc["areaStats"], doc["displacement"]

    def block(area, lens):
        return {x["label"]: x["value"] for x in stats[area][lens]}

    def zone_range(area):
        """The area's zone codes as a range, read off the survey paths. Kentron uses
        the lettered scheme ("Zone K01"), the older areas plain numbers."""
        codes = []
        for f in doc["features"]:
            if f["properties"].get("area") != area:
                continue
            m = re.search(r"\(Zone ([A-Za-z0-9]+)\)", f["properties"].get("name", ""))
            codes.append(m.group(1) if m else str(f["properties"].get("zone")))
        codes = sorted(set(codes), key=lambda s: (not s.isdigit(),
                                                  int(s) if s.isdigit() else s))
        return f"{codes[0]}–{codes[-1]}" if codes else "—"

    out = {"areas": {}, "displacement": disp}
    for key, label, date, weekday in SURVEY_AREAS:
        zones = zone_range(key)
        occ, ret, dsp = block(key, "occupancy"), block(key, "retained"), block(key, "displacement")
        dur = stats[key]["profile"]["duration"]
        feats = [f["properties"] for f in doc["features"]
                 if f["properties"].get("area") == key]
        out["areas"][key] = {
            "label": label, "date": date, "weekday": weekday, "zones": zones,
            "paths": len(feats),
            "spaces": sum(p.get("space") or 0 for p in feats),
            "peak_pct": occ["Peak Occupancy % (cap-weighted)"],
            # Area-wide peak hour: the most vehicles standing in the area at ONE clock
            # hour, over capacity. The cap-weighted figure above instead sums each
            # zone's own busiest hour, which double-counts across hours and is what the
            # 12 Aug ADB review took apart. Both are kept; the reports now lead with
            # this one. See peak_hour_pct/peak_hour.
            **_peak_hour(stats[key]["profile"]["vap"],
                         sum(p["space"] for p in feats
                             if p.get("peak_occupancy") is not None and p.get("space"))),
            "over85_pct": occ["% Zones Over 85% (Peak)"],
            "over_capacity": occ["Zones Over Capacity"],
            "retained": ret["Retained Spaces"],
            "removed": ret["Removed Spaces"],
            "retained_pct": ret["% Spaces Retained"],
            "displaced": dsp["Cars Displaced (Peak Hour)"],
            "absorb_onstreet": dsp["Nearby On-Street"],
            "absorb_offstreet": dsp["Nearby Off-Street"],
            "absorbed_onstreet_pct": dsp["% Absorbed On-Street"],
            "absorbed_total_pct": dsp["% Absorbed Total"],
            "displaced_pct": pct(dsp["Cars Displaced (Peak Hour)"], dsp["Spaces Removed"], 0),
            "stay": {k: dur[k] for k in ("shortPct", "errandPct", "workerPct", "alldayPct")},
            "avg_stay_h": dur["avg"],
            # Turnover on all bay types (see _turnover for why not road-edge only),
            # plus the road-edge figure and its denominator so the report can be
            # explicit about which is which.
            "turnover": _turnover(feats),
            "turnover_road_edge": _turnover(feats, road_edge_only=True),
            "road_edge_spaces": sum(
                p["space"] for p in feats
                if p.get("location") == "on-street"
                and p.get("parking_events") is not None and p.get("space")),
            "yard": SURVEY_YARDS[key],
        }

    allb = {lens: block("all", lens) for lens in ("occupancy", "retained", "displacement")}
    dur = stats["all"]["profile"]["duration"]
    out["all"] = {
        "peak_pct": allb["occupancy"]["Peak Occupancy % (cap-weighted)"],
        "peak_hour_cars": sum(a["peak_hour_cars"] for a in out["areas"].values()),
        "peak_hour_pct": round(100.0 * sum(a["peak_hour_cars"] for a in out["areas"].values())
                               / sum(f["properties"]["space"] for f in doc["features"]
                                     if f["properties"].get("peak_occupancy") is not None
                                     and f["properties"].get("space"))),
        "peak_hour": None,   # the six areas peak at different hours; see per-area figures
        "over85_pct": allb["occupancy"]["% Zones Over 85% (Peak)"],
        "over_capacity": allb["occupancy"]["Zones Over Capacity"],
        "removed": disp["removed_supply"],
        "displaced": disp["removed_demand"],
        "displaced_pct": pct(disp["removed_demand"], disp["removed_supply"], 0),
        "absorbed_onstreet_pct": disp["absorbed_onstreet"],
        "absorbed_total_pct": disp["absorbed"],
        "absorb_onstreet": disp["absorb_onstreet"],
        "absorb_offstreet": disp["absorb_offstreet"],
        "surveyed_zones": disp["removed_zones"],
        "stay": {k: dur[k] for k in ("shortPct", "errandPct", "workerPct", "alldayPct")},
        "avg_stay_h": dur["avg"],
        "hourly": stats["all"]["profile"]["vap"],
    }
    # Turnover range across the six areas, all bay types. The road-edge-only range
    # that the June reports and the July ADB deck quote as "5-11" is carried too, so
    # the difference can be explained rather than silently replaced.
    out["all"]["turnover_lo"] = min(a["turnover"] for a in out["areas"].values())
    out["all"]["turnover_hi"] = max(a["turnover"] for a in out["areas"].values())
    out["all"]["turnover_road_edge_lo"] = min(a["turnover_road_edge"]
                                              for a in out["areas"].values())
    out["all"]["turnover_road_edge_hi"] = max(a["turnover_road_edge"]
                                              for a in out["areas"].values())
    # Off-street dependency of the displacement balance: the share of the counted
    # absorptive capacity that is off-street rather than kerbside (1,935 of 2,326).
    # Stable across every revision of this file.
    out["all"]["absorb_capacity"] = disp["absorb_capacity"]
    out["all"]["offstreet_dependency_pct"] = pct(
        out["all"]["absorb_offstreet"], disp["absorb_capacity"], 0)
    # Kept under the old key too — several call sites still read it.
    out["all"]["yard_dependency_pct"] = out["all"]["offstreet_dependency_pct"]

    # typology of the surveyed supply itself (marked configuration, per zone)
    feats = [f["properties"] for f in doc["features"]]
    out["supply_typology"] = {}
    for key in ("regulation", "method", "location", "retained"):
        c = Counter()
        for p in feats:
            c[p.get(key)] += p.get("space") or 0
        out["supply_typology"][key] = dict(c)

    # 60 since the 24 Aug worksheet repair: displaced demand 1,120 -> 1,123 against
    # the same 1,886 spaces removed, so the share rounds up from 59%.
    assert out["all"]["displaced_pct"] == 60, out["all"]["displaced_pct"]
    # 92 since the 24 Aug worksheet repair (was 93; three zone-hours corrected).
    assert out["all"]["peak_pct"] == 92, out["all"]["peak_pct"]
    return out


@lru_cache(maxsize=1)
def yards():
    """The six surveyed off-street facilities. `peak_occupancy` in the GeoJSON is a
    vehicle COUNT, not a percentage, so the peak share is derived here rather than
    read — quoting the raw field as a percentage is an easy mistake to make."""
    path = os.path.join(WGS, "field-survey-yards.geojson")
    label = {v: k for k, v in {
        "kentron": "NalbandyanYard001", "komitas": "KomitasCity", "garegin": "GNOFF",
        "mega": "Palace", "malatia": "SebastiaYard006", "shiraz": "ShirazYard010",
    }.items()}
    rows = {}
    for f in _load(path):
        p = f["properties"]
        area = label.get(p["name"])
        if area is None:
            continue
        cap = int(p["space"])
        rows[area] = {
            "name": SURVEY_YARDS[area], "spaces": cap,
            "avg_pct": p["occupancy_pct"],
            "peak_vehicles": p["peak_occupancy"],
            "peak_pct": round(100.0 * p["peak_occupancy"] / cap),
            "unique_vehicles": p["unique_vehicles"],
        }
    total = sum(r["spaces"] for r in rows.values())
    weighted = round(sum(r["avg_pct"] * r["spaces"] for r in rows.values()) / total)
    out = {"areas": rows, "total_spaces": total, "weighted_avg_pct": weighted}
    out["at_or_over_capacity"] = sorted(
        (a for a, r in rows.items() if r["peak_pct"] >= 100),
        key=lambda a: -rows[a]["peak_pct"])
    assert total == 427, total
    return out


# ---------------------------------------------------------------------------
# vehicle-level typology (raw workbooks)
# ---------------------------------------------------------------------------
CODE_VEHICLE = {"C": "sedan", "T": "truck", "M": "motorcycle"}
CODE_LOCATION = {"OS": "carriageway", "FP": "footpath", "SB": "setback"}
CODE_METHOD = {"PA": "parallel", "A": "angled45", "PP": "perpendicular"}


def _code(value, table):
    if value is None:
        return None
    return table.get(str(value).strip().split()[0].upper().rstrip("-"))


@lru_cache(maxsize=1)
def vehicles():
    """Per-area and overall tallies of how vehicles ACTUALLY parked, plus a
    stationary-vehicle proxy. One row of "United Data" = one vehicle seen in one
    zone at one hour, so these are sighting-weighted shares, which is what the
    reports quote ("55% parked parallel", "13.0% on footpaths")."""
    import openpyxl

    out = {"areas": {}, "all": None}
    totals = defaultdict(Counter)
    stationary_all = {"candidates": 0, "vehicles": 0}

    for area, rel in WORKBOOKS.items():
        wb = openpyxl.load_workbook(os.path.join(ROOT, rel), read_only=True, data_only=True)
        ws = wb["United Data"]
        tally = defaultdict(Counter)
        # plate -> set(hours) for on-street rows only, for the stationary proxy
        plate_hours = defaultdict(set)
        hours = set()
        off = OFF_LABEL[area]
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i < 2 or row is None:
                continue
            time, zone, plate, vtype, loc, method, legal = (list(row) + [None] * 7)[:7]
            if not isinstance(time, (int, float)):
                continue
            on_street = isinstance(zone, (int, float))
            if not on_street and not (isinstance(zone, str)
                                      and zone.strip().lower() == off):
                continue
            group = "onstreet" if on_street else "offstreet"
            tally[group + "_total"]["n"] += 1
            # Vehicle-type share is quoted on "all classified vehicles surveyed in
            # the area", which includes the off-street log; the kerb-behaviour
            # shares (method / location / legality) are on-street only.
            tally["vehicle_all"][_code(vtype, CODE_VEHICLE)] += 1
            if on_street:
                hours.add(int(time))
                tally["vehicle"][_code(vtype, CODE_VEHICLE)] += 1
                tally["location"][_code(loc, CODE_LOCATION)] += 1
                tally["method"][_code(method, CODE_METHOD)] += 1
                tally["legal"]["illegal" if str(legal or "").strip()[:1].upper() == "I"
                               else "legal"] += 1
                p = str(plate or "").strip().lower()
                if p and p not in ("-", "none"):
                    plate_hours[p].add(int(time))
        wb.close()

        window = len(hours)
        # A vehicle seen in EVERY hour of the window never left the kerb all day —
        # the cheapest observable proxy for a stored or derelict vehicle.
        stationary = sum(1 for hs in plate_hours.values() if len(hs) == window)
        classified = sum(v for k, v in tally["vehicle_all"].items() if k)
        out["areas"][area] = {
            "sightings": tally["onstreet_total"]["n"],
            "classified": classified,
            "trucks": tally["vehicle_all"]["truck"],
            "truck_pct": pct(tally["vehicle_all"]["truck"], classified),
            "window_hours": window,
            "vehicle": dict(tally["vehicle"]),
            "location": dict(tally["location"]),
            "method": dict(tally["method"]),
            "legal": dict(tally["legal"]),
            "distinct_plates": len(plate_hours),
            "stationary_all_window": stationary,
            "stationary_pct": pct(stationary, len(plate_hours)),
        }
        for k in ("vehicle", "vehicle_all", "location", "method", "legal"):
            totals[k].update(tally[k])
        totals["onstreet_total"].update(tally["onstreet_total"])
        stationary_all["candidates"] += len(plate_hours)
        stationary_all["vehicles"] += stationary

    n = totals["onstreet_total"]["n"]
    classified = sum(v for k, v in totals["vehicle_all"].items() if k)
    out["all"] = {
        "sightings": n,
        "classified": classified,
        "trucks": totals["vehicle_all"]["truck"],
        "truck_pct": pct(totals["vehicle_all"]["truck"], classified),
        "vehicle": dict(totals["vehicle"]),
        "location": dict(totals["location"]),
        "method": dict(totals["method"]),
        "legal": dict(totals["legal"]),
        "distinct_plates": stationary_all["candidates"],
        "stationary_all_window": stationary_all["vehicles"],
        "stationary_pct": pct(stationary_all["vehicles"], stationary_all["candidates"]),
        "shares": {
            group: {k: pct(v, n) for k, v in totals[group].items() if k}
            for group in ("vehicle", "location", "method", "legal")
        },
    }
    return out


if __name__ == "__main__":
    s, f = supply(), survey()
    print("SUPPLY (Corridors 1+2, v2 conceptual design)")
    print(f"  total {s['total']:,} = on-street {s['on_street']:,} "
          f"({s['on_street_segments']} segments) + off-street {s['off_street']:,} "
          f"({s['off_street_facilities']} facilities)")
    print(f"  on-corridor {s['on_corridor']:,} | cross-street {s['cross_street']:,}")
    print(f"  removed {s['removed']:,} ({s['removed_pct']:.0f}%) | "
          f"retained {s['retained']:,} ({s['retained_pct']:.0f}%)")
    for cor, c in s["corridors"].items():
        print(f"    {cor}: {c['existing']:,} existing, {c['retained']} retained, "
              f"{c['removed']:,} removed | cross {c['cross_street']} | off {c['off_street']:,}")
    print(f"  zones {s['zones']}")
    print(f"  methods {s['methods']} | locations {s['locations']}")
    print(f"  signage {s['signage_yes']:,} ({pct(s['signage_yes'], s['on_corridor']):.1f}%) | "
          f"marking {s['marking_yes']:,} ({pct(s['marking_yes'], s['on_corridor']):.1f}%)")
    print(f"  Zone A streets {s['zone_a_streets'][:5]}")
    print()
    print("SURVEY (six areas)")
    a = f["all"]
    print(f"  peak {a['peak_pct']}% | over-85 {a['over85_pct']}% | "
          f"{a['over_capacity']} zones over capacity")
    print(f"  displaced {a['displaced']:,} / removed {a['removed']:,} = "
          f"{a['displaced_pct']}% | on-street absorption {a['absorbed_onstreet_pct']}% | "
          f"yard dependency {a['yard_dependency_pct']}%")
    print(f"  absorptive capacity {a['absorb_capacity']:,} = on-street "
          f"{a['absorb_onstreet']} + off-street courtyard {a['absorb_offstreet']:,} "
          f"({a['yard_dependency_pct']:.0f}%)")
    for k, v in f["areas"].items():
        print(f"    {v['label'][:26]:26s} peak {v['peak_pct']:3d}%  removed {v['removed']:4d}  "
              f"displaced {v['displaced']:4d} ({v['displaced_pct']:3.0f}%)  "
              f"on-street {v['absorbed_onstreet_pct']:3d}%  stay {v['avg_stay_h']}h  "
              f"turnover {v['turnover']}")
    print()
    print("VEHICLE TYPOLOGY (sighting-weighted)")
    v = vehicles()["all"]
    print(f"  {v['sightings']:,} sightings, {v['distinct_plates']:,} distinct plates")
    for g in ("method", "location", "vehicle", "legal"):
        print(f"  {g}: " + ", ".join(f"{k} {p:.1f}%" for k, p in
                                     sorted(v['shares'][g].items(), key=lambda kv: -kv[1])))
    print(f"  trucks {v['trucks']:,} of {v['classified']:,} classified = {v['truck_pct']}%")
    for a2, av in vehicles()["areas"].items():
        print(f"    {a2:9s} trucks {av['trucks']:4d}/{av['classified']:5d} = "
              f"{av['truck_pct']:4.1f}%   stationary {av['stationary_all_window']}")
    print(f"  present in every sweep: {v['stationary_all_window']:,} "
          f"({v['stationary_pct']:.1f}% of plates)")
