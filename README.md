# The Compliance Bouncer
### Nate Ambrad and Fem Jansen
### ECE576

## About the game
Students assume the role of Data Center Compliance Officer at a scaled-down computing facility. The facility provides a pre-recorded stream of jobs. Most are legitimate work, but some are attempts to train a “restricted” model above a set compute limit, disguising it as routine work. Our game uses its own governance threshold, invented for the game and not tied to any real-world regulation: no actor may exceed 2.3x10^12 training FLOPs or 4.6 kJ of training energy. The student is tasked to write a ```policy_checker()``` function that receives a signed evidence record for each job, verifies it, and then returns a verdict: either allow the job or block it. 

In real hardware-rooted design the chip is the source of trust. One way which chip validity can be quantified is through a PUF-derived key. This key can be used to sign chip meter readings, so a verifier can confirm which chip produced a report and that it was not altered, even if the operator controls the software stack. We are going to simulate this. Each simulated chip has a signing key, standing in for its PUF key, that only the instructor’s generator holds. Every record students receive is an integrity-protected evidence object: the values the chip measured (chip ID, job ID, counter, FLOPs, energy) are signed, while operator claims such as the declared workload type are not. Students will get a ```verify_signature()``` helper which returns true if a signature is valid and false if not, to keep the focus on what to check rather than on the cryptography of the key signature. Before ```policy_checker()``` applies thresholds, the students must write a short ```verify_evidence()``` function that checks:
- Endorsement: the chip is in the registry
- Integrity: the signature matches that chip’s public key
- Freshness: the counter is higher than the chip’s last accepted report. This stands in for a nonce, since pre-recorded data cannot answer a live challenge 

Records that pass are charged to the chip’s registered owner. Records that fail are blocked and never counted toward any total. A valid signature proves where the numbers came from and that they were not changed; it does not prove that unsigned claims are true or that the meter saw all of the work.

The student is provided with levels.json, which gives six integrity-protected evidence objects per game level, and game_config.json, which provides them with FLOP and energy limits as well as references ranges for training and inference workloads. There are four game levels in total, each increasing in complexity.
- Level 1 will contain only honest jobs, some very obviously over the limit, so a simple threshold check will catch them. It also includes two types of forged records: one whose FLOP value was edited after signing, and one signed by a chip that is not in the registry.
- Level 2 will introduce jobs that split a large run into many small chunks under different job IDs. Students must track cumulative compute per actor rather than per job. It also includes replayed records, where an actor resubmits an old, validly signed low-FLOP report, so students must track each chip’s counter. Totals are tracked by the chip’s registered owner, not by job ID.
- Level 3 introduces jobs whose declared workload type doesn’t match their measured profile. Students must check claims against reference ranges for that type. Because the declared type is unsigned, a valid signature says nothing about it. In the hardest case the backward pass runs in kernels the FLOP meter does not count, so the signed record under-reports FLOPs and only the energy data exposed it.
- Level 4 will introduce measurement noise and borderline legitimate jobs, so rigid thresholds start blocking innocent jobs. Policies must use justifiable tolerance bands instead of guesswork. Earlier forged and replayed records reappear as regression checks.

## Playing the game
After the student has written their ```verify_evidence()``` and ```policy_checker()``` functions inside student.py, they can run the game and get their scores. To run the game, the student must specify the level.
```bash
python play.py <level_number>
```
where <level_number> is 1, 2, 3, or 4.
The answer_keys.json file should not be provided to the student, it is for instructor use only.
