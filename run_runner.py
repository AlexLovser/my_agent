import sys

sys.stdout.reconfigure(encoding="utf-8")

from repository import print_db
from runner import Runner
from tools import insert_level, insert_space, update_level, update_space

TOOL_MAP = {
    "insert_level": insert_level,
    "insert_space": insert_space,
    "update_level": update_level,
    "update_space": update_space,
}

PAYLOAD = [
    {"tool": "insert_level", "args": {"name": "Rez-de-chaussée", "floor_number": 0}},
    {"tool": "insert_space", "args": {"name": "Cuisine", "level_id": "<id above>"}},
    {"tool": "update_space", "args": {"space_id": "<id above>", "non_visit_reason": "Pièce fermée à clé"}},
    {"tool": "update_space", "args": {"space_id": "<id above>", "name": "Cuisine ouverte"}},
    {"tool": "update_space", "args": {"space_id": "<id above>", "non_visit_reason": None}},
    {"tool": "insert_space", "args": {"name": "Chambre", "level_id": "lvl_does_not_exist"}},
    {"tool": "update_level", "args": {"level_id": "<id above>"}},
    {"tool": "insert_level", "args": {"floor_number": 1}},
]

if __name__ == "__main__":
    runner = Runner(tools=TOOL_MAP)
    results = runner.run(PAYLOAD)

    for result in results:
        print(result)

    print()
    print_db()
