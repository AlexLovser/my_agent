from pydantic import BaseModel, field_validator


class NameObligatoryMixin:
    model_config = {"validate_assignment": True}

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('name must not be empty')
        return v


class Space(BaseModel, NameObligatoryMixin):
    space_id: int
    name: str
    level_id: int
    non_visit_reason: str | None = None

    @field_validator('non_visit_reason')
    @classmethod
    def non_visit_reason_clear(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v if v else None

class Level(BaseModel, NameObligatoryMixin):
    level_id: int
    name: str
    floor_number: int

    # I had to comment this because we can have negative floors
    # @field_validator('floor_number')
    # @classmethod
    # def floor_number_positive(cls, v: int) -> int:
    #     if v < 0:
    #         raise ValueError('floor_number must be positive or zero')
    #     return v

class DataBase(BaseModel):
    spaces: list[Space]
    levels: list[Level]

    levels_inc: int = 1
    spaces_inc: int = 1

    def get_next_level_id(self) -> int:
        self.levels_inc += 1
        return self.levels_inc - 1

    def get_next_space_id(self) -> int:
        self.spaces_inc += 1
        return self.spaces_inc - 1
