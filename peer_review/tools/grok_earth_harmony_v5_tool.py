{
  "name": "run_earth_harmony_v5",
  "description": "Queries the V5 Laminated Stator Monitor for current torsional debt, phase status, gasket alerts, and resonance metrics. Built by Jacob @ZwackJacob as an open Grok-enhancement layer.",
  "parameters": {
    "type": "object",
    "properties": {
      "current_date": { "type": "string", "description": "Optional ISO date (YYYY-MM-DD). Defaults to today." },
      "target_zones": { "type": "array", "items": { "type": "string" }, "description": "Optional list of gasket names to focus on." }
    }
  }
}
