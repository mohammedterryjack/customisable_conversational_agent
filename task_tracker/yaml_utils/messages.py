from enum import Enum


class DefaultMessages(Enum):
    IMPOSSIBLE_TASK = [
        "I can't {task_name}",
        "I don't know how to {task_name} yet",
        "I know you want me to {task_name} but I can't right now",
    ]
    QUERY_SLOT_PROMPT = "I don't know the {slot_name}"


class WarningMessages(Enum):
    UNDECLARED_SLOT = "the task {task_name} uses an unspecified slot '{slot_name}' in '{text_with_slot}...'. It was included as a slot under the task's {field_name} field with {type_name} scope by default"
    IMPROPER_NAME = (
        "Task name {improper_name} should be camel case (i.e. {proper_name})"
    )
    REQUIRED_FIELD_TYPE_MISSING = "task {task_name}'s {field_name} field did not specify a {required_field_type} type"
    REQUIRED_FIELD_MISSING = "{required_field_name} field not specified for {task_name} task. Default Values set"


class ErrorMessages(Enum):
    INVALID_TRIGGER_CONDITION = "{trigger_condition} seems to be an invalid expression. Make sure all strings are enclosed in 'quotes' and supported conditional operators are used (e.g. and, or, ==, >=, etc)"
    ADDITIONAL_FIELD_TYPE_DETECTED = "'{additional_field_type}' is an unrecognised type for {task_name}: {field_name}:. Recognised types include: {expected_field_types}"
    UNDEFINED_SLOT = "the task {task_name} points to an unknown slot '{slot_name}' in '{text_with_slot}...'. Please declare this as a slot under Slots:"
    TEXT_CONTAINS_INVALID_CHARACTER = (
        "remove invalid character {invalid_character} from {text}"
    )
    UNEXPECTED_DATA_STRUCTURE = "{task_name}: {field_name}: {field_type}:... should have a {expected_data_structure}, but a {unexpected_data_structure} was found"
    UNRECOGNISED_VALUE = "{task_name}: {field_name}: {field_type}:... should have a value from {recognised_values}, but {unrecognised_value} was found"
    UNDEFINED_ACTION = "{task_name} references an undefined action: {action_name}.  Please add this to config/custom_actions.py"
