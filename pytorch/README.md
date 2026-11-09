# PyTorch Profiler FLOP Count and CPU Time Tracking
We measure the FLOP counts and CPU time of runs on an ML model with [PyTorch](https://docs.pytorch.org/docs/stable/profiler.html).

## Setup
Install PyTorch if you haven't already:
```bash
pip install torch --break-system-packages
```

# Run the profiler
```bash
python pytorch/profiler.py --who <name>
```

Results are saved to `pytorch/results/flops_<name>.csv`, so you never get merge conflicts
