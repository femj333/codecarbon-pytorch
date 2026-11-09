# Combined Runs -> CodeCarbon and PyTorch profiler
Here, you can run one training job with CodeCarbon and torch.profiler together, and the results are saved in 1 JSON file.

## To run a training job:
```bash
python combined_runs/record_run.py --tag <run_name> --who <user_name> --steps <num_steps>
```

Writes to ```combined_runs/results/<user_name>_<run_name>.json```

## To summarize results:
```bash
python summarize_runs.py
```

Prints a summary table (grouped by workload type and step count) and writes:
    results/all_runs.json -> every run in one JSON file
    results/SUMMARY_RUNS.md -> every run in one Markdown file
