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

| File | Required for Game?   | What It Is |
|---|---|---|
| `game_data.json` | Yes | Game configuration + chip registry + signed records |
| `verify.py` | Yes | Contains helper function `verify_signature()` for student to use in `student.py` |
| `student.py` | Yes | Student implementation of `verify_evidence()` and `policy_checker()` |
| `codecarbon/` | No | Measure the energy use and CO2 emissions of PyTorch training runs (see `codecarbon/README.md`) |
| `pytorch/` | No | Measure the FLOP counts and CPU time of runs on an ML model with PyTorch (see `pytorch/README.md`)  |
| `combined_runs/` | No | Run one training job with CodeCarbon and PyTorch together (see `combined_runs/README.md`) |

## Play

The game is graded with gradescope. Use entry code G78P6J and submit your completed `verify_evidence()` and 
`policy_checker()` functions in a file called `student.py` to the 'Compliance Bouncer' assignment to view your score.

https://www.gradescope.com/courses/1446177/assignments/9033003
