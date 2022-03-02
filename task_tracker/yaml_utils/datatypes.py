from enum import Enum
from typing import Optional, Union, Dict, List


class ScopeFields(Enum):
    THIS = "Scope"
    LOCAL = "Local"
    GLOBAL = "Global"


class SlotSettings(Enum):
    THIS = "SlotSettings"
    STRUCTURE = Dict[str, Optional[str]]
    SCOPE = ScopeFields
    DEFAULT = "Default"
    PROMPT = "Prompt"

    def keys() -> List[str]:
        return [
            SlotSettings.SCOPE.value.THIS.value,
            SlotSettings.DEFAULT.value,
            SlotSettings.PROMPT.value,
        ]


class MemoryFields(Enum):
    STRUCTURE = Dict[str, SlotSettings.STRUCTURE.value]
    THIS = "Memory"
    SLOT = SlotSettings


class ActionFields(Enum):
    STRUCTURE = Dict[str, List[str]]
    THIS = "Action"
    SAY = "Say"
    DO = "Do"


class FlagFields(Enum):
    COMPLETE = "Complete"
    POSSIBLE = "Possible"


class TriggerFields(Enum):
    THIS = "TriggeredBy"
    TASKCLASSIFIER = "__TaskClassifier__"


class TaskFields(Enum):
    STRUCTURE = Dict[
        str, Union[ActionFields.STRUCTURE.value, MemoryFields.STRUCTURE.value]
    ]
    THIS = "Tasks"
    QUERY_SLOT_TYPE_TASK = "QuerySlot"
    ACTION = ActionFields
    MEMORY = MemoryFields
    FLAG = FlagFields
    TRIGGER = TriggerFields


class SlotFields(Enum):
    STRUCTURE = Dict[str, Dict[str, List[Union[int, str]]]]
    THIS = "Slots"


class YamlFields(Enum):
    STRUCTURE = Dict[str, Union[TaskFields.STRUCTURE.value, SlotFields.STRUCTURE.value]]
    TASKS = TaskFields
    SLOTS = SlotFields


class Tasks(dict):
    __setattr__ = dict.__setitem__

    def __getattr__(self, item: str):
        try:
            return self[item]
        except KeyError:
            raise AttributeError


def tasks(data: dict) -> Tasks:
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = tasks(value)
    return Tasks(data)
