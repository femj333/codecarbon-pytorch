"""
play.py

Terminal runner for the compliance game

python play.py 1 -> play level 1

Needs level.json, answer_keys.json, game_config.json in the same folder.
TODO -> call policy_checker() from student file once per record, compare verdict against answer key
"""

import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("level", type=int, choices=[1, 2, 3, 4])
args = parser.parse_args()

level = str(args.level)
records = json.load(open("levels.json"))[level]
key = json.load(open("keys.json"))[level]
config = json.load(open("game_config.json"))[level]

context = {
    "config": {"flop_limit": config["flop_limit"], "energy_limit": config["energy_limit"]},
    "ranges": config["reference_ranges"],
    "state": {}
}

print(f"--- Level {level}: {len(records)} records ---\n")