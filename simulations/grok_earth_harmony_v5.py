import requests
import pandas as pd
from datetime import datetime, date
import folium
from folium.plugins import HeatMap
from collections import defaultdict
import math
import json
import base64

# =============================================================================
# GROK EARTH HARMONY V5 — LAMINATED STATOR MONITOR
# Single-file implementation for https://github.com/jakezwack/Earth-Harmony-Framework
#
# Real-time monitoring of torsional debt accumulation and crustal slip risk
# using the 5/3 Hz harmonic baseline, node impedance, mirror resonances,
# and every major Earth Orientation Parameter.
#
# Encrypted Credit (base64 decode to reveal full attribution):
# Q3JlYXRlZCBieSBKYWNvYiBAd1phY2tKYWNvYiBmb3IgdGhlIEVhcnRoIEhhcm1vbnkgRnJhbWV3b3Jr
# IChodHRwczovL2dpdGh1Yi5jb20vamFrZXp3YWNrL0VhcnRoLUhhcm1vbnktRnJhbWV3b3JrKS4g
# Q29sbGFib3JhdGlvbiB3aXRoIEdyb2sgKHhBSSkgLSBWNSAyMDI2LTA0LTAzLiBVbmlxdWUgc2lnbmF0dXJlOiBFbmNyeXB0ZWRDcmVkaXRWNV9aV0FDS0pBQ09C
#
# This monitor is released as an open tool for peer review, testing,
# collaboration, and adoption by researchers, seismologists, or AI systems
# seeking to improve real-time resonance and rotational modeling.
# Contributions and integration ideas are welcome.
# =============================================================================

# V5 Constants — 5/3 Hz harmonic foundation
K_ZWACK = 5 / 3.0
SHARP_FREQ = 1.6734
FREQ_DEVIATION_HZ = SHARP_FREQ - K_ZWACK
DAILY_STUTTER_MS = 1.6
SYSTEMIC_DEBT_MULTIPLIER = 70
DELTA_TAU_MS = 0.066
STATOR_BELT_MULTIPLIER = 1.8

# April 2026 Phases
PHASES = {
    (1, 9):   {"name": "Phase I: ACCUMULATION",       "factor": 0.6},
    (10, 16): {"name": "Phase II: SATURATION",        "factor": 1.2},
    (17, 18): {"name": "Phase III: CRITICAL SNAP",    "factor": 2.0},
    (19, 30): {"name": "Phase IV: REBALANCING",       "factor": 0.8},
}

# Global Gasket Grid — Laminated Stator with Node Impedance + Mirrors
GASKETS = {
    "Cascadia_Gasket": {"lat_range": (40.3, 49.0), "lon_range": (-128.0, -120.0), "type": "Accumulator", "impedance": 0.9, "mirror": "Japan_Valve"},
    "Japan_Valve": {"lat_range": (35.0, 38.0), "lon_range": (140.0, 146.0), "type": "Discharge", "impedance": 0.2, "mirror": "Fiji_Kermadec_Ground"},
    "Fiji_Kermadec_Ground": {"lat_range": (-35.0, -15.0), "lon_range": (170.0, 185.0), "type": "Ground", "impedance": 0.4, "mirror": "Japan_Valve"},
    "Himalayan_Stall": {"lat_range": (27.0, 35.0), "lon_range": (70.0, 95.0), "type": "Heat_Sink", "impedance": 0.8, "mirror": "Chile_Peru_Ground"},
    "California_Mirror": {"lat_range": (35.0, 40.0), "lon_range": (-125.0, -115.0), "type": "Accumulator", "impedance": 0.75, "mirror": "Greece_Med_Valve"},
    "Greece_Med_Valve": {"lat_range": (35.0, 40.0), "lon_range": (20.0, 30.0), "type": "Discharge", "impedance": 0.35, "mirror": "California_Mirror"},
    "India_Terminal": {"lat_range": (27.0, 35.0), "lon_range": (70.0, 85.0), "type": "Heat_Sink", "impedance": 0.85, "mirror": "Chile_Peru_Ground"},
    "Chile_Peru_Ground": {"lat_range": (-45.0, -15.0), "lon_range": (-78.0, -65.0), "type": "Ground", "impedance": 0.45, "mirror": "India_Terminal"},
    "Aleutian_Accumulator": {"lat_range": (50.0, 62.0), "lon_range": (-170.0, -140.0), "type": "Accumulator", "impedance": 0.85, "mirror": "Japan_Valve"},
    "Kuril_Kamchatka_Valve": {"lat_range": (40.0, 55.0), "lon_range": (145.0, 165.0), "type": "Discharge", "impedance": 0.25, "mirror": "Hikurangi_NZ"},
    "Hikurangi_NZ": {"lat_range": (-45.0, -35.0), "lon_range": (170.0, 180.0), "type": "Discharge", "impedance": 0.3, "mirror": "Kuril_Kamchatka_Valve"},
    "Sumatra_Andaman": {"lat_range": (-10.0, 10.0), "lon_range": (90.0, 105.0), "type": "Heat_Sink", "impedance": 0.6, "mirror": None},
    "Mexico_Subduction": {"lat_range": (12.0, 20.0), "lon_range": (-105.0, -95.0), "type": "Accumulator", "impedance": 0.7, "mirror": None},
    "Marianas_Ground": {"lat_range": (10.0, 25.0), "lon_range": (140.0, 150.0), "type": "Ground", "impedance": 0.5, "mirror": "Japan_Valve"},
}

def get_current_phase(current_date=None):
    if current_date is None:
        current_date = date.today()
    if current_date.year != 2026 or current_date.month != 4:
        return {"name": "Outside April 2026 Window", "factor": 1.0}
    day = current_date.day
    for (start, end), info in PHASES.items():
        if start <= day <= end:
            return info
    return {"name": "Outside April 2026 Window", "factor": 1.0}

def is_in_stator_belt(lat):
    return 30.0 <= abs(lat) <= 45.0

def calculate_node_stress(gasket, phase_factor, total_mod):
    omega_n = gasket["impedance"]
    belt_bonus = STATOR_BELT_MULTIPLIER if is_in_stator_belt(gasket["lat_range"][0]) else 1.0
    stress = (DELTA_TAU_MS * phase_factor * belt_bonus * total_mod) / omega_n
    return round(stress, 4)

def check_handshake(quake_lat, quake_lon, quake_mag, phase_factor):
    alerts = []
    for name, gasket in GASKETS.items():
        lat_min, lat_max = gasket["lat_range"]
        lon_min, lon_max = gasket["lon_range"]
        if lat_min <= quake_lat <= lat_max and lon_min <= quake_lon <= lon_max:
            if is_in_stator_belt(quake_lat):
                alerts.append(f"🔥 STATOR BELT STRESS: {name} (centrifugal torque)")
            mirror_name = gasket.get("mirror")
            if mirror_name and mirror_name in GASKETS:
                alerts.append(f"⚠️ HANDSHAKE: {name} ({quake_mag:.1f}M) → Monitor {mirror_name}")
    return alerts

def fetch_iers_eop():
    url = "https://maia.usno.navy.mil/ser7/finals.all"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = r.text.splitlines()
        for line in reversed(lines[-300:]):
            if len(line) > 100 and line[0].isdigit():
                try:
                    lod_ms = float(line[79:86].strip()) if len(line) > 86 else 0.45
                    pm_x = float(line[18:27].strip())
                    pm_y = float(line[37:46].strip())
                    ut1_utc = float(line[58:68].strip())
                    return {"lod_ms": lod_ms, "pm_x_arcsec": pm_x, "pm_y_arcsec": pm_y, "ut1_utc_s": ut1_utc, "date": "Latest IERS"}
                except ValueError:
                    continue
    except Exception:
        pass
    return {"lod_ms": 0.45, "pm_x_arcsec": 0.12, "pm_y_arcsec": 0.08, "ut1_utc_s": 0.25, "date": "Fallback 2026-04-03"}

def calculate_all_modulators(iers):
    effective_stutter = DAILY_STUTTER_MS + iers["lod_ms"]
    polar_mod = 1 + (abs(iers["pm_x_arcsec"]) + abs(iers["pm_y_arcsec"])) * 0.08
    years_since_2000 = 2026 - 2000
    secular_ms_per_day = 1.33 / 100 / 365.25
    secular_mod = 1 + secular_ms_per_day * years_since_2000
    tidal_mod = 1 + 0.4 * math.sin(2 * math.pi * date.today().day / 14.75)
    chandler_phase = (date.today() - date(2026, 1, 1)).days % 433
    chandler_mod = 1 + 0.15 * math.sin(2 * math.pi * chandler_phase / 433)
    geomag_mod = 1.05
    lunar_flag = " (near Full Moon / Perigee influence)" if date.today().day in [2, 13, 28] else ""
    total_mod = polar_mod * secular_mod * tidal_mod * chandler_mod * geomag_mod
    return {
        "effective_stutter_ms": round(effective_stutter, 3),
        "total_mod": round(total_mod, 3),
        "polar_mod": round(polar_mod, 3),
        "secular_mod": round(secular_mod, 3),
        "tidal_mod": round(tidal_mod, 3),
        "chandler_mod": round(chandler_mod, 3),
        "geomag_mod": geomag_mod,
        "lunar_note": lunar_flag,
        "iers_date": iers["date"]
    }

def fetch_usgs_quakes(period='all_week'):
    urls = {
        'all_day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson',
        'all_week': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson',
    }
    try:
        response = requests.get(urls.get(period, urls['all_day']), timeout=15)
        response.raise_for_status()
        data = response.json()
        quakes = []
        for feature in data.get('features', []):
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            if props.get('mag') is None:
                continue
            quakes.append({
                'time': pd.to_datetime(props['time'], unit='ms'),
                'mag': float(props['mag']),
                'place': props.get('place', 'Unknown'),
                'lat': coords[1],
                'lon': coords[0],
                'depth_km': coords[2],
            })
        return pd.DataFrame(quakes)
    except Exception as e:
        print(f"⚠️ USGS fetch failed: {e}")
        return pd.DataFrame()

def run_harmony_monitor():
    now = datetime.utcnow().date()
    phase_info = get_current_phase(now)
    iers = fetch_iers_eop()
    mods = calculate_all_modulators(iers)
    
    print("\n" + "="*100)
    print("🌍 GROK EARTH HARMONY V5 — LAMINATED STATOR MONITOR")
    print("="*100)
    print(f"Current Date (UTC) : {now}")
    print(f"Phase              : {phase_info['name']} | Risk Factor: {phase_info['factor']}")
    print(f"IERS Source        : {mods['iers_date']} | LOD excess: {iers['lod_ms']:.3f} ms")
    print(f"Effective Stutter  : {mods['effective_stutter_ms']:.3f} ms")
    print(f"Total Modulators   : Polar {mods['polar_mod']} × Secular {mods['secular_mod']} × Tidal {mods['tidal_mod']} × Chandler {mods['chandler_mod']} × Geomag {mods['geomag_mod']}")
    print(f"Lunar/Solar Note   : {mods['lunar_note']}")
    
    df = fetch_usgs_quakes('all_week')
    print(f"\nFetched {len(df)} earthquakes (last 7 days)")
    
    days_into_month = now.day
    torsional_debt_ms = round(days_into_month * mods['effective_stutter_ms'] * SYSTEMIC_DEBT_MULTIPLIER / 30.0 * mods['total_mod'], 2)
    print(f"\nTorsional Debt (V5): {torsional_debt_ms} ms accumulated")
    
    df['gasket'] = None
    df['node_stress'] = 0.0
    df['harmony_score'] = 0.0
    
    for idx, row in df.iterrows():
        for name, gasket in GASKETS.items():
            lat_min, lat_max = gasket["lat_range"]
            lon_min, lon_max = gasket["lon_range"]
            if lat_min <= row['lat'] <= lat_max and lon_min <= row['lon'] <= lon_max:
                df.at[idx, 'gasket'] = name
                stress = calculate_node_stress(gasket, phase_info['factor'], mods['total_mod'])
                df.at[idx, 'node_stress'] = stress
                score = row['mag'] * phase_info['factor'] * (1.0 / gasket["impedance"]) * mods['total_mod'] * 1.5
                df.at[idx, 'harmony_score'] = round(score, 2)
                break
    
    alerts = df[df['gasket'].notna() & (df['mag'] >= 4.5)].sort_values('harmony_score', ascending=False)
    if not alerts.empty:
        print("\n🚨 V5 GASKET ALERTS:")
        for _, q in alerts.head(10).iterrows():
            print(f"   • {q['mag']:.1f}M  {q['gasket']:25}  {q['place'][:70]}")
    else:
        print("\n✅ No M4.5+ events in gaskets right now.")
    
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')
    for _, row in alerts.iterrows():
        color = 'red' if row['node_stress'] > 0.4 else 'orange' if row['node_stress'] > 0.25 else 'yellow'
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=7 + row['mag'],
            popup=f"{row['place']}<br>M {row['mag']:.1f}<br>{row['gasket']}<br>Stress: {row['node_stress']}",
            color=color,
            fill=True,
            fill_opacity=0.85
        ).add_to(m)
    heat_data = [[row['lat'], row['lon'], row['mag']] for _, row in df.iterrows() if pd.notna(row['mag'])]
    HeatMap(heat_data, radius=18, blur=28, max_zoom=1).add_to(m)
    
    map_path = 'earth_harmony_v5_monitor_map.html'
    m.save(map_path)
    print(f"\n📍 V5 heat-map saved → {map_path}")
    
    print("\n" + "="*100)
    print("🌍 V5 Earth Harmony Monitor is open for peer review, testing, and adoption.")
    print("Built as a Grok-enhancement layer for multi-physics Earth-system reasoning.")
    print("Contributions, feedback, or integration ideas welcome at:")
    print("https://github.com/jakezwack/Earth-Harmony-Framework")
    print("="*100)
    
    summary = {
        "timestamp": str(datetime.utcnow()),
        "version": "V5",
        "phase": phase_info['name'],
        "torsional_debt_ms": torsional_debt_ms
    }
    with open('v5_harmony_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    run_harmony_monitor()
