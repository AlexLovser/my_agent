from models import DataBase, Level, Space
from errors import *

db: DataBase | None = None
def init_db():
    return DataBase(
        spaces=[],
        levels=[],
    )

def get_db():
    global db
    if db is None:
        db = init_db()
    return db


def print_db():
    for i in get_db().levels:
        print(i)
        for j in get_db().spaces:
            if j.level_id == i.level_id:
                print('\t', j)

        print()


########################################################################################
# Level methods
########################################################################################

def _get_level_by_name(*, name: str):
    db = get_db()

    for level in db.levels:
        if level.name == name:
            return level

    raise LevelDoesNotExist()


def _get_level_by_id(*, level_id: int):
    db = get_db()

    for level in db.levels:
        if level.level_id == level_id:
            return level

    raise LevelDoesNotExist()

def _get_floor_numbers() -> list[int]:
    db = get_db()
    return [level.floor_number for level in db.levels]


def get_level(*, name: str | None = None, level_id: int | None = None, raise_exception: bool):
    if name is not None and level_id is not None:
        raise ValueError("You cant provide both name and level_id")

    try:
        if name is not None:
            return _get_level_by_name(name=name)

        if level_id is not None:
            return _get_level_by_id(level_id=level_id)
    except LevelDoesNotExist:
        if raise_exception:
            raise
        return None

    raise ValueError("Either name or level_id must be provided")


def insert_level(*, name: str, floor_number: int):
    db = get_db()

    # I would use upsert/atomic ops here, but since it is SYNC,
    # there is no need to do it

    if get_level(name=name, raise_exception=False) is not None:
        raise LevelAlreadyExists()

    # Cant have the same floor number as another level
    if floor_number in _get_floor_numbers():
        raise LevelWithThisFloorNumberAlreadyExists()

    level_id = db.get_next_level_id()

    level = Level(
        level_id=level_id,
        name=name,
        floor_number=floor_number,
    )
    db.levels.append(level)
    return level


def update_level(*,level_id: int, name: str | None = None, floor_number: int | None = None):
    existing = get_level(level_id=level_id, raise_exception=False)

    if not existing:
        raise LevelDoesNotExist()

    if name is not None:
        existing.name = name

    if floor_number is not None:
        existing.floor_number = floor_number

    # No commit because "existing" is already the reference

    return existing


########################################################################################
# Space methods
########################################################################################

def _get_space_by_name(*, name: str):
    db = get_db()

    for space in db.spaces:
        if space.name == name:
            return space

    raise SpaceDoesNotExist()


def _get_space_by_id(*, space_id: int):
    db = get_db()

    for space in db.spaces:
        if space.space_id == space_id:
            return space

    raise SpaceDoesNotExist()

def filter_spaces_by_level_id(*, level_id: int):
    db = get_db()

    # Not using generators for consistency

    # Can be empty if level does not exists
    return [space for space in db.spaces if space.level_id == level_id]

def get_space(*, name: str | None = None, space_id: int | None = None, raise_exception: bool):
    if name is not None and space_id is not None:
        raise ValueError("You cant provide both name and space_id")

    try:
        if name is not None:
            return _get_space_by_name(name=name)

        if space_id is not None:
            return _get_space_by_id(space_id=space_id)
    except SpaceDoesNotExist:
        if raise_exception:
            raise
        return None

    raise ValueError("Either name or space_id must be provided")


def insert_space(name: str, level_id: int, non_visit_reason: str | None = None):
    db = get_db()

    other_spaces = filter_spaces_by_level_id(level_id=level_id)

    for space in other_spaces:
        if space.name == name:
            # Cant have the same space on the same floor (removable)
            raise FloorAndNameCombinationAlreadyExists()

    get_level(level_id=level_id, raise_exception=True)

    space_id = db.get_next_space_id()

    space = Space(
        space_id=space_id,
        name=name,
        level_id=level_id,
        non_visit_reason=non_visit_reason,
    )
    db.spaces.append(space)
    return space


def update_space(*, space_id: int, **changes):
    current_space = get_space(space_id=space_id, raise_exception=True)

    if current_space is None:
        raise SpaceDoesNotExist() # Just for linter (we'll get exception if  space doesnot exists)

    new_name = changes.get("name", current_space.name)
    new_level_id = changes.get("level_id", current_space.level_id)

    if new_name is not None:
        new_name = new_name.strip()

    if "name" in changes or "level_id" in changes:
        get_level(level_id=new_level_id, raise_exception=True)
        other_spaces = filter_spaces_by_level_id(level_id=new_level_id)

        for space in other_spaces:
            if space.space_id == current_space.space_id:
                continue
            if space.name == new_name:
                raise FloorAndNameCombinationAlreadyExists()

    if "name" in changes:
        current_space.name = new_name

    if "level_id" in changes:
        current_space.level_id = new_level_id

    if "non_visit_reason" in changes:
        current_space.non_visit_reason = changes["non_visit_reason"]

    # No commit because "current_space" is already the reference

    return current_space
