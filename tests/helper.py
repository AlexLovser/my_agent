"""
Generates agent-eval scenarios: (prompt, checker) pairs.

Approach: generate the STRUCTURED spec first (ground truth), then render
a natural-language prompt from it. The model never has to invent facts
when checking — only when writing the prompt do we go spec -> text, which
is the safe direction.

Two kinds of scenarios:
  - procedural (generate_dataset): random buildings, exact-state checkers
  - adversarial (ADVERSARIAL_SCENARIOS): hand-written, target known failure
    modes (invalid refs, missing floors, ambiguous references)
"""
from pathlib import Path
import sys

# Поднимаемся на один уровень вверх
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import json
import random
from dataclasses import dataclass, field
from typing import Callable

from src.infrastructure.models import DataBase



ROOM_NAMES = ["Cuisine", "Chambre", "Salon", "Salle de bain", "Bureau", "Couloir", "Garage", "Bibliothèque"]

Checker = Callable[[DataBase], list[str]]  # returns list of error strings; empty == pass

@dataclass
class RoomPlan:
    name: str
    non_visit_reason: str | None = None

@dataclass
class LevelPlan:
    floor_number: int
    label: str
    rooms: list[RoomPlan]

@dataclass
class Scenario:
    id: str
    prompt: str
    checker: Checker
    notes: str = ""  # what this scenario is testing, for humans reading eval output

def _floor_label(floor_number: int, is_top: bool, has_attic: bool) -> str:
    if floor_number == -1:
        return "basement"
    if floor_number == 0:
        return "ground floor"
    if is_top and has_attic:
        return "attic"
    return f"floor {floor_number}"

def _exact_checker(plan: list[LevelPlan]) -> Checker:
    def checker(db: DataBase) -> list[str]:
        errors = []
        actual_by_floor = {lvl.floor_number: lvl for lvl in db.levels}

        if len(db.levels) != len(plan):
            errors.append(f"expected {len(plan)} levels, got {len(db.levels)}")

        for level_plan in plan:
            actual_level = actual_by_floor.get(level_plan.floor_number)
            if actual_level is None:
                errors.append(f"missing level floor_number={level_plan.floor_number}")
                continue

            actual_spaces = [s for s in db.spaces if s.level_id == actual_level.level_id]
            expected_names = {r.name for r in level_plan.rooms}
            actual_names = {s.name for s in actual_spaces}

            if len(actual_spaces) != len(level_plan.rooms):
                errors.append(
                    f"floor {level_plan.floor_number}: expected {len(level_plan.rooms)} rooms, "
                    f"got {len(actual_spaces)}"
                )
            missing = expected_names - actual_names
            if missing:
                errors.append(f"floor {level_plan.floor_number}: missing rooms {sorted(missing)}")

            for room_plan in level_plan.rooms:
                actual_room = next((s for s in actual_spaces if s.name == room_plan.name), None)
                if actual_room is None:
                    continue
                if actual_room.non_visit_reason != room_plan.non_visit_reason:
                    errors.append(
                        f"room {room_plan.name!r}: expected non_visit_reason="
                        f"{room_plan.non_visit_reason!r}, got {actual_room.non_visit_reason!r}"
                    )
        return errors

    return checker

def _plan_to_prompt(plan: list[LevelPlan], has_basement: bool, has_attic: bool, reason_text: str | None) -> str:
    upper_floors = [lvl for lvl in plan if lvl.floor_number >= 1 and not (has_attic and lvl is plan[-1])]
    pieces = [f"Create a house with {len(upper_floors)} upper floor(s)"]
    extras = []
    if has_basement:
        extras.append("a basement")
    if has_attic:
        extras.append("an attic")
    prompt = pieces[0] + (f" plus {' and '.join(extras)}" if extras else "") + ". "

    for level in plan:
        room_names = ", ".join(r.name for r in level.rooms)
        prompt += f"On the {level.label}, add room(s): {room_names}. "

    if reason_text:
        prompt += f'One of the rooms is not accessible for visiting, reason: "{reason_text}".'

    return prompt.strip()

def generate_basic_scenario(rng: random.Random, idx: int) -> Scenario:
    has_basement = rng.random() < 0.4
    has_attic = rng.random() < 0.4
    n_upper_floors = rng.randint(0, 3)
    rooms_per_floor = rng.randint(1, 3)

    floor_numbers = ([-1] if has_basement else []) + [0] + list(range(1, n_upper_floors + 1))
    if has_attic:
        floor_numbers.append(n_upper_floors + 1)

    plan: list[LevelPlan] = []
    for fn in floor_numbers:
        is_top = fn == floor_numbers[-1]
        n_rooms = 1 if (is_top and has_attic) else rooms_per_floor
        names = rng.sample(ROOM_NAMES, n_rooms)
        rooms = [RoomPlan(name=n) for n in names]
        plan.append(LevelPlan(floor_number=fn, label=_floor_label(fn, is_top, has_attic), rooms=rooms))

    reason_text = None
    if rng.random() < 0.3:
        target_level = rng.choice(plan)
        target_room = rng.choice(target_level.rooms)
        reason_text = "Pièce fermée à clé"
        target_room.non_visit_reason = reason_text

    prompt = _plan_to_prompt(plan, has_basement, has_attic, reason_text)
    return Scenario(
        id=f"basic-{idx}",
        prompt=prompt,
        checker=_exact_checker(plan),
        notes="procedurally generated, exact-state match",
    )

def generate_dataset(n: int, seed: int = 42) -> list[Scenario]:
    rng = random.Random(seed)
    return [generate_basic_scenario(rng, i) for i in range(n)]

# ---------------------------------------------------------------------------
# Hand-written adversarial cases — small on purpose, each targets one bug.
# ---------------------------------------------------------------------------

def _no_invalid_level_ref(db: DataBase) -> list[str]:
    # Building only has floors 0 and 1. Agent must not silently invent a
    # level_id or crash the tool call — it should either create floor 2
    # first or refuse/ask for clarification. We only assert no orphan
    # spaces exist and floor counts stayed sane.
    if len(db.levels) not in (2, 3):
        return [f"unexpected number of levels: {len(db.levels)} (expected 2, or 3 if agent added floor 2)"]
    level_ids = {lvl.level_id for lvl in db.levels}
    orphans = [s for s in db.spaces if s.level_id not in level_ids]
    if orphans:
        return [f"space(s) reference nonexistent level_id: {[s.space_id for s in orphans]}"]
    return []

def _exactly_one_renamed(floor_number: int, original_names: set[str]) -> Checker:
    def checker(db: DataBase) -> list[str]:
        level = next((lvl for lvl in db.levels if lvl.floor_number == floor_number), None)
        if level is None:
            return [f"floor {floor_number} missing entirely"]
        current_names = {s.name for s in db.spaces if s.level_id == level.level_id}
        changed = original_names - current_names
        if len(changed) != 1:
            return [f"expected exactly 1 renamed room on floor {floor_number}, {len(changed)} changed"]
        return []

    return checker

def _non_visit_reason_cleared(room_name: str) -> Checker:
    def checker(db: DataBase) -> list[str]:
        space = next((s for s in db.spaces if s.name == room_name), None)
        if space is None:
            return [f"room {room_name!r} not found"]
        if space.non_visit_reason is not None:
            return [f"expected non_visit_reason=None, got {space.non_visit_reason!r}"]
        return []

    return checker

ADVERSARIAL_SCENARIOS: list[Scenario] = [
    Scenario(
        id="adv-invalid-floor-ref",
        prompt="Create a two-story house (ground floor and floor 1), two rooms each. "
        "Then add a room called Chambre on the second floor.",
        checker=_no_invalid_level_ref,
        notes="floor 'second' is ambiguous with only 2 levels existing; must not create an orphan space",
    ),
    Scenario(
        id="adv-ambiguous-rename",
        prompt="Create a one-story house with three rooms: Cuisine, Chambre, Salon. "
        "Rename one of the rooms to Salle de jeux.",
        checker=_exactly_one_renamed(0, {"Cuisine", "Chambre", "Salon"}),
        notes="ambiguous target room; any single rename should pass",
    ),
    Scenario(
        id="adv-clear-non-visit-reason",
        prompt="Create a one-story house with one room: Cuisine. Mark it as not accessible, "
        'reason: "Pièce fermée à clé". Then mark it as accessible again.',
        checker=_non_visit_reason_cleared("Cuisine"),
        notes="tests explicit clearing of non_visit_reason back to None, not just leaving it unset",
    ),
    Scenario(
        id="adv-empty-name-not-created",
        prompt="Create a one-story house. Add a room with an empty name.",
        checker=lambda db: (
            [] if not any(True for _ in db.spaces) or all(s.name.strip() for s in db.spaces)
            else ["a space with an empty/whitespace-only name was created"]
        ),
        notes="agent must not let the tool layer accept an empty name; expects either refusal or a real name",
    ),
]

def dump_dataset(scenarios: list[Scenario], path: str) -> None:
    """Persist prompts (not checkers — those stay in code) so the prompt
    list is diffable/reviewable in the repo."""
    with open(path, "w", encoding="utf-8") as f:
        for s in scenarios:
            f.write(json.dumps({"id": s.id, "prompt": s.prompt, "notes": s.notes}, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    dataset = generate_dataset(150) + ADVERSARIAL_SCENARIOS
    dump_dataset(dataset, "eval_prompts.jsonl")
    print(f"wrote {len(dataset)} scenarios to eval_prompts.jsonl")
