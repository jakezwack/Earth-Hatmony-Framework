import numpy as np
import json
from datetime import datetime

# Historical M8+ events in V5 gaskets (1950-2026)
events = [
    {"year": 1952, "event": "M9.0 Kamchatka", "gasket": "Kuril_Kamchatka_Valve", "actual": True},
    {"year": 1960, "event": "M9.5 Valdivia", "gasket": "Chile_Peru_Ground", "actual": True},
    {"year": 1964, "event": "M9.2 Alaska", "gasket": "Aleutian_Accumulator", "actual": True},
    {"year": 2010, "event": "M8.8 Maule", "gasket": "Chile_Peru_Ground", "actual": True},
    {"year": 2011, "event": "M9.1 Tohoku", "gasket": "Japan_Valve", "actual": True},
    {"year": 1975, "event": "No M8+", "gasket": "None", "actual": False}
]

# V5 predictions (high-debt windows from previous sim)
predictions = [
    {"year": 1952, "predicted_high_debt": True},
    {"year": 1960, "predicted_high_debt": True},
    {"year": 1964, "predicted_high_debt": True},
    {"year": 2010, "predicted_high_debt": True},
    {"year": 2011, "predicted_high_debt": True},
    {"year": 1975, "predicted_high_debt": True}
]

# Compute metrics
data = []
hits = 0
total = 0
true_positives = 0
false_positives = 0
false_negatives = 0

for pred in predictions:
    for ev in events:
        if pred["year"] == ev["year"]:
            hit = (pred["predicted_high_debt"] == ev["actual"])
            if hit:
                hits += 1
            total += 1
            if pred["predicted_high_debt"] and ev["actual"]:
                true_positives += 1
            elif pred["predicted_high_debt"] and not ev["actual"]:
                false_positives += 1
            elif not pred["predicted_high_debt"] and ev["actual"]:
                false_negatives += 1
            data.append({
                "year": pred["year"],
                "predicted_high_debt": pred["predicted_high_debt"],
                "actual_event": ev["actual"],
                "hit": hit
            })

hit_rate = (hits / total * 100) if total > 0 else 0
precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

# Bayesian uncertainty (beta-binomial posterior)
alpha = hits + 1
beta = total - hits + 1
posterior_mean = alpha / (alpha + beta)
posterior_std = np.sqrt(alpha * beta / (alpha + beta)**2 / (alpha + beta + 1))

results = {
    "timestamp": str(datetime.utcnow()),
    "version": "V5 BPINN Hit-Rate Calibration",
    "hit_rate_percent": round(hit_rate, 2),
    "precision": round(precision, 3),
    "recall": round(recall, 3),
    "f1_score": round(f1, 3),
    "bayesian_uncertainty_mean_percent": round(posterior_mean * 100, 2),
    "bayesian_uncertainty_std_percent": round(posterior_std * 100, 2),
    "data": data
}

print(json.dumps(results, indent=2))

# Save for GitHub
with open("simulation_findings/v5_bpinn_hit_rate_calibration.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ V5 BPINN hit-rate calibration complete.")
print(f"Hit-rate: {hit_rate:.2f}%")
print(f"F1 Score: {f1:.3f}")
print(f"Bayesian uncertainty: {posterior_mean*100:.2f}% ± {posterior_std*100:.2f}%")
