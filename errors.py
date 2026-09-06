
class AppError(Exception):
    message = "<Not Implemented Message Text>"

    def __str__(self):
        return self.message

class LevelDoesNotExist(AppError):
    message = "Level you are trying to get does not exist"

class LevelAlreadyExists(AppError):
    message = "Level you are trying to createalready exists"

class LevelWithThisFloorNumberAlreadyExists(AppError):
    message = "Level with this floor number already exists"

class SpaceDoesNotExist(AppError):
    message = "Space you are trying to get does not exist"

class SpaceAlreadyExists(AppError):
    message = "Space you are trying to create already exists"

class FloorAndNameCombinationAlreadyExists(AppError):
    message = "There is already a space with the same name on this floor"




class ToolCallError(Exception):
    """Raised when a tool call payload can't be resolved or executed."""
