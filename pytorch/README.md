# PyTorch Profiler FLOP Count and CPU Time Tracking
We measure the FLOP counts and CPU time of runs on an ML model with [PyTorch](https://docs.pytorch.org/docs/stable/profiler.html).

## Setup
Install PyTorch if you haven't already:
```bash
pip install torch --break-system-packages
```

# Run the profiler
```bash
python pytorch_profiler_demo.py
```

Currently, the profiler runs on a tiny MLP model. To change the model, optimizer, or loss function, edit the `build_model` function. To change the training data images or labels, edit the `build_data` function.
