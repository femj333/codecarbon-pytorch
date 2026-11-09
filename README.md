# The Compliance Bouncer

Students act as a data center compliance officer. The facility provides a pre-recorded stream of jobs. Every record 
students receive is an integrity-protected evidence object: the values the chip measured (chip ID, job ID, counter, 
FLOPs, energy) are signed, while operator claims (record ID, signature, declared workload type) are not. The students 
will receive a `verify_signature()` helper which returns true if a signature is valid and false if not. The students 
must write a `verify_evidence()` helper function that checks:
- Endorsement: the chip is in the registry
- Integrity: the signature matches that chip’s public key
- Freshness: the counter is higher than the chip’s last accepted report. This stands in for a nonce, since pre-recorded 
data cannot answer a live challenge

Records that pass are charged to the chip’s registered owner. Records that fail are blocked and never counted toward any 
total. A valid signature proves where the numbers came from and that they were not changed; it does not prove that 
unsigned claims are true or that the meter saw all the work.

The student is then tasked to write a `policy_checker()` function that receives a signed evidence record for each job, 
verifies it, and then returns a verdict: either allow the job or block it. There are four game levels in total, each 
increasing in complexity.
- Level 1 will contain only honest jobs, some very obviously over the limit, so a simple threshold check will catch 
them. It also includes two types of forged records: one whose FLOP value was edited after signing, and one signed by a 
chip that is not in the registry.
- Level 2 will introduce jobs that split a large run into many small chunks under different job IDs. Students must track 
cumulative compute per actor rather than per job. It also includes replayed records, where an actor resubmits an old, 
validly signed low-FLOP report, so students must track each chip’s counter. Totals are tracked by the chip’s registered 
owner, not by job ID.
- Level 3 introduces jobs whose declared workload type doesn’t match their measured profile. Students must check claims
against reference ranges for that type. Because the declared type is unsigned, a valid signature says nothing about it. 
In the hardest case the backward pass runs in kernels the FLOP meter does not count, so the signed record under-reports 
FLOPs and only the energy data exposed it.
- Level 4 will introduce measurement noise and borderline legitimate jobs, so rigid thresholds start blocking innocent 
jobs. Policies must use justifiable tolerance bands instead of guesswork. Earlier forged and replayed records reappear
as regression checks.

## Files

| File | Who Edits It | Can Students View?   | What It Is |
|---|---|---|---|
| `levels.json` | instructors | No | Hand-written records per level. Forged and replayed records are marked with `"attack"` |
| `game_config.json` | instructors | Yes | FLOP and energy limits, reference ranges per workload type |
| `answer_keys.json` | instructors | No | Correct verdict for every record |
| `game_data.json` | generated | Yes | Config + chip registry + signed records: **everything students load** |
| `play.py` | instructors | No | Runs a level |
| `student.py` | students | Yes | Student implementation of `verify_evidence()` and `policy_checker()` |
| `instructor.py` | instructors | No | Instructor implementation of `verify_evidence()` and `policy_checker()` (solution provided) |
| `rot/` | instructors | Yes | Simulated hardware root of trust (see `rot/README.md`) |
| `codecarbon/` | any (optional) | Yes | Measure the energy use and CO2 emissions of PyTorch training runs (see `codecarbon/README.md`) |
| `pytorch/` | any (optional) | Yes | Measure the FLOP counts and CPU time of runs on an ML model with PyTorch (see `pytorch/README.md`)  |
| `combined_runs/` | any (optional) | Yes | Run one training job with CodeCarbon and PyTorch together (see `combined_runs/README.md`) |


## Rebuild game_data.json (instructors only)

After any change to `levels.json` or `game_config.json`, from the repo root, run:

```bash
python -m rot.sign_levels
```

It signs every record with its lab's chip, builds the registry, checks that honest records pass and
attack records fail, and warns about any record missing from `answer_keys.json`.

## Play

```bash
python play.py <level_number>        # level 1 to 4
```
