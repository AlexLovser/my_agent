from pydantic import BaseModel
from utils.config import settings

from src.app_agents.base_agent import BaseAgent
from src.infrastructure.tools import(
    get_level,
    get_space,
    insert_level,
    insert_space,
    update_level as _update_level,
    update_space as _update_space
)

# I had to implement this wrap to getting optional params as None
class UpdateLevelInput(BaseModel):
    level_id: int
    name: str | None = None
    floor_number: int | None = None


class UpdateSpaceInput(BaseModel):
    space_id: int
    name: str | None = None
    level_id: int | None = None
    non_visit_reason: str | None = None


def update_level(payload: UpdateLevelInput):
    kwargs = {"level_id": payload.level_id}

    if "name" in payload.model_fields_set:
        kwargs["name"] = payload.name
    if "floor_number" in payload.model_fields_set:
        kwargs["floor_number"] = payload.floor_number

    return _update_level(**kwargs)


def update_space(payload: UpdateSpaceInput):
    kwargs = {"space_id": payload.space_id}

    if "name" in payload.model_fields_set:
        kwargs["name"] = payload.name
    if "level_id" in payload.model_fields_set:
        kwargs["level_id"] = payload.level_id
    if "non_visit_reason" in payload.model_fields_set:
        kwargs["non_visit_reason"] = payload.non_visit_reason

    return _update_space(**kwargs)


class ImageAgent(BaseAgent):
    SYSTEM_PROMPT = (
        "You manage house levels and spaces only through the provided tools. Tool outputs are the source of truth. "
        "Never invent data or assume ids: use only ids returned by successful tool calls. Dependent actions must be "
        "done step by step; independent actions may be batched only after the required ids are known. "
        "If a tool returns an error, that action failed. Do not describe it as completed, do not create substitute "
        "objects, and do not retry the same impossible action more than once unless the user asks for a workaround. "
        "If the user asks to rename a room on a specific floor, rename a room that already exists on that floor and "
        "do not move it unless explicitly asked. Interpret 'on each floor' as numbered floors only, not basement or "
        "attic, unless the user says otherwise; do not add basement rooms unless explicitly requested. "
        "Before replying, reconcile your answer with the successful tool calls from this turn. Report only what was "
        "actually completed, and clearly separate anything failed or impossible with the reason. Do not claim full "
        "completion unless every requested action was confirmed by successful tool results."
        "---"
        "You can get an image with a scheme of a house, so if he asks you you have to implement it in a db with provided tools"
    )
    model_name = settings.model_name
    token = settings.openai_api_key

    def __init__(self):
        tools = [
            get_level,
            get_space,
            insert_level,
            insert_space,
            update_level,
            update_space,
        ]
        super().__init__(tools=tools)
