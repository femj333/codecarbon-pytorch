# Combined Runs -> CodeCarbon and PyTorch profiler
Here, you can run one training job with CodeCarbon and torch.profiler together, and the results are saved in 1 json file.

To run a training job:
```bash
python record_run.py --tag <run_name> --who <user_name> --steps <num_steps>
```

Writes to ```results/<user_name>_<run_name>.json```

To change the model or data, edit ```build_model()``` and ```build_data()```
