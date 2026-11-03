"""
summarize_runs.py

combine every results/*.json from record_run.py

python summarize_runs.py

Prints a summary table (grouped by workload type and step count) and writes:
    results/all_runs.json -> every run in one json file
    results/SUMMARY_RUNS.md -> every run in one markdown file
"""

import json
import statistics
from collections import defaultdict
from pathlib import Path

results_dir = Path("results")
runs = []
for path in sorted(results_dir.glob("*.json")):
    if path.name == "all_runs.json":
        continue
    data = json.loads(path.read_text())
    if "pytorch" in data and "codecarbon" in data:
        data["file"] = path.name
        runs.append(data)

if not runs:
    raise SystemExit("No runs found")

(results_dir / "all_runs.json").write_text(json.dumps(runs, indent=2))

groups = defaultdict(list)
for r in runs:
    groups[(r["workload_type"], r["steps"])].append(r)

lines = ["| Type | Steps | Runs | FLOPs (mean) | FLOPs spread | Energy kJ (mean) | Energy kJ (spread) | FLOPs per kJ |",
         "|---|---|---|---|---|---|---|---|"]

mean_flops = {}
for (wtype, steps), rs in sorted(groups.items()):
    flops= [r["pytorch"]["total_flops"] for r in rs]
    energy = [r["codecarbon"]["energy_kj"] for r in rs]
    mf, me = statistics.mean(flops), statistics.mean(energy)
    mean_flops[(wtype, steps)] = mf
    flop_spread = (max(flops) - min(flops)) / mf * 100
    energy_spread = (max(energy) - min(energy)) / me * 100
    lines.append(f"| {wtype} | {steps} | {len(rs)} | {mf:,.0f} | {flop_spread:.1f}% | {me:.4f} | {energy_spread:.0f} | {mf / me:,.0f} |")

table = "\n".join(lines)
print(table)

(results_dir / "SUMMARY_RUNS.md").write_text(table + "\n")
print(f"\n{len(runs)} runs combined -> results/all_runs.json, results/SUMMARY_RUNS.md")