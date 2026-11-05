"""
play.py

Terminal runner for the compliance game

python play.py 1 -> play level 1

Needs game_data.json and answer_keys.json in the same folder.
game_data.json (config + chip registry + signed records) is built from
levels.json and game_config.json by: python -m rot.sign_levels
TODO -> call policy_checker() from student file once per record, compare verdict against answer key
"""

import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("level", type=int, choices=[1, 2, 3, 4])
args = parser.parse_args()

level = str(args.level)
game = json.load(open("game_data.json"))
records = game["levels"][level]
key = json.load(open("answer_keys.json"))[level]
config = game["config"]

context = {
    "config": {"flop_limit": config["flop_limit"], "energy_limit_kj": config["energy_limit_kj"]},
    "ranges": config["reference_ranges"],
    "registry": game["registry"],   # chip_id -> {"public_key", "owner"}
    "state": {}
}

print(f"--- Level {level}: {len(records)} records ---\n")