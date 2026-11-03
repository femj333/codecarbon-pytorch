"""
record_run.py

Run one training job with CodeCarbon and torch.profiler together, save both results in 1 json file

python record_run.py --tag <run_name> --who <user_name> --steps <num_steps>

Writes to results/<user_name>_<run_name>.json

To change the model or data, edit build_model() and build_data()
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import torch
import torch.nn as nn
from codecarbon import OfflineEmissionsTracker
from torch.profiler import profile, ProfilerActivity

# --- model -----------
def build_model():
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(28 * 28, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )
    return model, torch.optim.SGD(model.parameters(), lr=0.01), nn.CrossEntropyLoss()

# -- data ------------
def build_data(batch_size=32):
    return torch.randn(batch_size, 1, 28, 28), torch.randint(0, 10, (batch_size,))

# -- arguments ----------
parser = argparse.ArgumentParser()
parser.add_argument('--tag', required=True)
parser.add_argument('--who', required=True)
parser.add_argument('--steps', type=int, default=200)
parser.add_argument('--mode', choices=["training", "inference"], default="training")
args = parser.parse_args()

# -- build model and data ---------
model, optimizer, loss_fn = build_model()
images, labels = build_data()

# -- track emissions -----
tracker = OfflineEmissionsTracker(country_iso_code="USA",
                                save_to_file=False,
                                log_level="error")
tracker.start()
with profile(activities=[ProfilerActivity.CPU], record_shapes=True,
            with_flops=True) as prof:
    if args.mode == "training": # training mode
        model.train()
        for _ in range(args.steps):
            optimizer.zero_grad()
            loss_fn(model(images), labels).backward()
            optimizer.step()
    else: # inference mode
        model.eval()
        with torch.no_grad():
            for _ in range(args.steps):
                model(images)
tracker.stop()

# -- get total flops -------
total_flops = sum(e.flops for e in prof.key_averages())

# -- get codecarbon data ------
cc = tracker.final_emissions_data
energy_kwh = cc.energy_consumed

# -- format results ------
result = {
    "who": args.who,
    "tag": args.tag,
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "workload_type": args.mode,
    "steps": args.steps,
    "pytorch": {"total_flops": total_flops},
    "codecarbon": {"duration_s": round(cc.duration, 2),
                   "energy_wh": round(energy_kwh * 1000, 4),
                   "energy_kj": round(energy_kwh * 3600, 6),
                    "co2eq_g": round(cc.emissions * 1000, 4),
                   },
}

# -- store results as json ----------
Path("results").mkdir(exist_ok=True)
out = Path("results") / f'{args.who}_{args.tag}.json'
json_dump = json.dumps(result, indent=2)
out.write_text(json_dump)
print(f'Saved {out}')
print(json_dump)
