from pydantic import BaseModel
from config import settings

from app_agents.base_agent import BaseAgent
from tools import(
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


class MainAgent(BaseAgent):
    SYSTEM_PROMPT = (
        "You are an assistant that works with the database only through the provided tools. "
        "When you need to create or update data, call the relevant tool instead of inventing results."
    )
    model_name = settings.model_name
    token = settings.chat_gpt_key

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
