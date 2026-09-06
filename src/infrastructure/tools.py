from pydantic import ValidationError, BaseModel
from utils.dto import Response, Status
from utils.errors import *
import src.infrastructure.repository as Repo
import functools
import logging
import sys

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

UNSET = object()


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"CALL {func.__name__}(args={args}, kwargs={kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.info(f"RETURN {func.__name__} -> {result}")
            return result
        except Exception as e:
            logger.exception(f"ERROR in {func.__name__}: {e}")
            raise
    return wrapper

def error_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValidationError, ValueError) as e:
            print(e)
            return Response(message=f"Validation error: {e}", data=[], status=Status.ERROR)
        except AppError as e:
            print(e)
            return Response(message=str(e), data=[], status=Status.ERROR)
    return wrapper


def dto_to_json(dto: BaseModel) -> str:
    return dto.model_dump_json()


def dto_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return dto_to_json(result)
    return wrapper

########################################################################################
# Level tools
########################################################################################

@log_call
@dto_decorator
@error_decorator
def get_level(*, name: str | None = None, level_id: int | None = None):
    """
        Get a level by name or level_id.

        Returns:
            Response: A response object containing the level data or an error message.
    """

    result = Repo.get_level(name=name, level_id=level_id, raise_exception=True)
    if result:
        return Response(message="Level found", data=[result], status=Status.SUCCESS)
    return Response(message="Level not found", data=[], status=Status.ERROR)



@log_call
@dto_decorator
@error_decorator
def insert_level(name: str | None = None, floor_number: int | None = None):
    """
    Create a new level.

    Args:
        name (str): The name of the level.
        floor_number (int): The floor number of the level.

    Returns:
        Response: A response object containing the created level data or an error message.
    """
    if name is None:
        raise ValueError("name is required")
    if floor_number is None:
        raise ValueError("floor_number is required")

    result = Repo.insert_level(name=name, floor_number=floor_number)
    return Response(message="Level created", data=[result], status=Status.SUCCESS)

@log_call
@dto_decorator
@error_decorator
def update_level(level_id: int, name: str | None = None, floor_number: int | None = None):
    """
    Update an existing level.

    Args:
        level_id (int): The ID of the level to update.
        name (str | None): The new name of the level.
        floor_number (int | None): The new floor number of the level.

    Returns:
        Response: A response object containing the updated level data or an error message.
    """
    repo_kwargs = {"level_id": level_id}
    if name is not None:
        repo_kwargs["name"] = name
    if floor_number is not None:
        repo_kwargs["floor_number"] = floor_number

    result = Repo.update_level(**repo_kwargs)
    return Response(message="Level updated", data=[result], status=Status.SUCCESS)

########################################################################################
# Space methods
########################################################################################

@log_call
@dto_decorator
@error_decorator
def get_all_spaces_on_the_level(*, level_id: int, limit: int | None = None):
    """
    Get all spaces on a given level.

    Args:
        level_id (int): The ID of the level to retrieve spaces from.
        limit (int | None): The maximum number of spaces to return.

    Returns:
        Response: A response object containing the spaces data or an error message.
    """
    Repo.get_level(level_id=level_id, raise_exception=True) # Raise if level does not exist

    result = Repo.filter_spaces_by_level_id(level_id=level_id)
    if limit is not None:
        result = result[:limit]
    return Response(message="Spaces found", data=result, status=Status.SUCCESS)

@log_call
@dto_decorator
@error_decorator
def get_space(*, name: str | None = None, space_id: int | None = None):
    """
    Get a space by its name or ID.

    Args:
        name (str | None): The name of the space to retrieve.
        space_id (int | None): The ID of the space to retrieve.

    Returns:
        Response: A response object containing the space data or an error message.
    """
    result = Repo.get_space(name=name, space_id=space_id, raise_exception=True)
    if result:
        return Response(message="Space found", data=[result], status=Status.SUCCESS)
    return Response(message="Space not found", data=[], status=Status.ERROR)


@log_call
@dto_decorator
@error_decorator
def insert_space(*, name: str | None = None, level_id: int | None = None, non_visit_reason: str | None = None):
    """
    Create a new space.

    Args:
        name (str): The name of the space.
        level_id (int): The ID of the level to associate with the space.
        non_visit_reason (str | None): The reason for not visiting the space.

    Returns:
        Response: A response object containing the created space data or an error message.
    """
    if name is None:
        raise ValueError("name is required")
    if level_id is None:
        raise ValueError("level_id is required")

    result = Repo.insert_space(name=name, level_id=level_id, non_visit_reason=non_visit_reason)
    return Response(message="Space created", data=[result], status=Status.SUCCESS)


@log_call
@dto_decorator
@error_decorator
def update_space(*, space_id: int, name: str | None = None, level_id: int | None = None, non_visit_reason=UNSET):
    """
    Update an existing space.

    Args:
        space_id (int): The ID of the space to update.
        name (str | None): The new name of the space.
        level_id (int | None): The new level ID of the space.
        non_visit_reason (str | None): The new non-visit reason of the space.

    Returns:
        Response: A response object containing the updated space data or an error message.
    """
    repo_kwargs = {"space_id": space_id}
    if name is not None:
        repo_kwargs["name"] = name
    if level_id is not None:
        repo_kwargs["level_id"] = level_id
    if non_visit_reason is not UNSET:
        repo_kwargs["non_visit_reason"] = non_visit_reason

    result = Repo.update_space(**repo_kwargs)
    return Response(message="Space created", data=[result], status=Status.SUCCESS)
