# Bench-Top Resonance Test Protocol
**Exact 1.673419 Hz Test on Sioux Quartzite (or Konark-style resonator)**

**Goal:** Produce a 30-second video showing measurable weight/friction change at the exact predicted frequency.

**Required Parts (now in your kit):**
- DDS Function Generator (set to exactly 1.673419 Hz sine wave)
- 35 mm piezo ceramic disc
- HX711 load cell + Arduino (0.01 g resolution)
- Sioux Quartzite sample (or 3D-printed replica)
- Phone for video recording

**Step-by-Step Instructions:**

1. Glue piezo disc to the bottom of the quartzite sample.
2. Wire piezo → driver board → DDS generator.
3. Place sample on HX711 load cell (tare scale to 0).
4. Set DDS to **exact 1.673419 Hz** sine wave (low amplitude first).
5. Start video recording:
   - Show DDS screen clearly displaying "1.673419 Hz"
   - Show scale reading (tared)
   - Turn on signal
   - Film any weight drop, oscillation, or friction change
6. Repeat 3–5 times at increasing amplitudes.
7. Save raw video + CSV data from HX711.

**Success Criteria:**
Any repeatable change ≥0.01 g at exactly 1.673419 Hz = positive result.

**Upload:**
- Video to YouTube (unlisted) or directly to repo
- Raw CSV to `/data/`
- Add video link to this README

**Next:** When you film it, we add the video link and raw data to the repo.
