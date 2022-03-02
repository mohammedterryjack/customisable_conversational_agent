from typing import List, Generator
from string import punctuation, Formatter
from yaml import safe_load, YAMLError
from warnings import warn
from copy import deepcopy

from task_tracker.yaml_utils.datatypes import YamlFields, Tasks, tasks
from task_tracker.yaml_utils.messages import (
    ErrorMessages,
    WarningMessages,
    DefaultMessages,
)
from task_tracker.config import custom_actions

with open("task_tracker/yaml_utils/default.yml") as default_file:
    DEFAULT = tasks(safe_load(default_file))


class YamlLoader:
    """
    loads in custom Yaml File
    """

    @staticmethod
    def safe_load_tasks(path: str) -> Tasks:
        """
        loads in yaml file and
        ensures tasks are formatted correctly etc
        """
        with open(path) as datafile:
            data = safe_load(datafile)
        YamlLoader.check_data(data)
        return tasks(data)

    @staticmethod
    def check_data(data: YamlFields.STRUCTURE.value) -> None:
        if (
            YamlFields.TASKS.value.THIS.value not in data
            or data[YamlFields.TASKS.value.THIS.value] is None
        ):
            warn(
                WarningMessages.REQUIRED_FIELD_MISSING.value.format(
                    required_field_name=YamlFields.TASKS.value.THIS.value,
                    task_name="",
                )
            )
            data[YamlFields.TASKS.value.THIS.value] = {}
        if (
            YamlFields.SLOTS.value.THIS.value not in data
            or data[YamlFields.SLOTS.value.THIS.value] is None
        ):
            warn(
                WarningMessages.REQUIRED_FIELD_MISSING.value.format(
                    required_field_name=YamlFields.SLOTS.value.THIS.value,
                    task_name="",
                )
            )
            data[YamlFields.SLOTS.value.THIS.value] = {}
        YamlLoader.check_slots_data(slotdata=data[YamlFields.SLOTS.value.THIS.value])
        YamlLoader.add_slot_query_tasks(data)
        YamlLoader.check_task_data(
            taskdata=data[YamlFields.TASKS.value.THIS.value],
            declared_slots=data[YamlFields.SLOTS.value.THIS.value].keys(),
        )

    @staticmethod
    def check_slots_data(slotdata: YamlFields.TASKS.value.STRUCTURE.value) -> None:
        """
        ensuere slot data is formatted correctly
        """
        if not isinstance(slotdata, dict):
            raise YAMLError(
                ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                    task_name=YamlFields.SLOTS.value.THIS.value,
                    field_name="",
                    field_type="",
                    expected_data_structure=dict,
                    unexpected_data_structure=type(slotdata),
                )
            )
        for slot in slotdata:
            YamlLoader.check_slot_data(slot=slot, slot_data=slotdata)

    @staticmethod
    def check_slot_data(
        slot: str, slot_data: YamlFields.SLOTS.value.STRUCTURE.value
    ) -> None:
        """
        ensure each slot is formatted correctly
        ---
        Slots:
            name: [100]
            transportation:
                - car
                - bus
                - bike
        ---
        """
        if isinstance(slot_data[slot], list) and any(slot_data[slot]):
            if len(slot_data[slot]) == 1:
                if isinstance(slot_data[slot][0], int) or isinstance(
                    slot_data[slot][0], float
                ):
                    return
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=YamlFields.SLOTS.value.THIS.value,
                        field_name=slot,
                        field_type=slot_data[slot][0],
                        expected_data_structure=f"{int} or {float}",
                        unexpected_data_structure=type(slot_data[slot][0]),
                    )
                )
            for value in slot_data[slot]:
                if isinstance(value, str):
                    continue
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=YamlFields.SLOTS.value.THIS.value,
                        field_name=slot,
                        field_type=value,
                        expected_data_structure=str,
                        unexpected_data_structure=type(value),
                    )
                )
            return
        raise YAMLError(
            ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                task_name=YamlFields.SLOTS.value.THIS.value,
                field_name=slot,
                field_type=slot_data[slot],
                expected_data_structure=list,
                unexpected_data_structure=type(slot_data[slot]),
            )
        )

    @staticmethod
    def check_task_data(
        taskdata: YamlFields.TASKS.value.STRUCTURE.value, declared_slots: List[str]
    ) -> None:
        """
        ensure task data is formatted correctly
        """
        if not isinstance(taskdata, dict):
            raise YAMLError(
                ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                    task_name=YamlFields.TASKS.value.THIS.value,
                    field_name="",
                    field_type="",
                    expected_data_structure=dict,
                    unexpected_data_structure=type(taskdata),
                )
            )
        for task_name in taskdata:
            YamlLoader.check_task_name(task_name=task_name)
            if taskdata[task_name] is None:
                taskdata[task_name] = deepcopy(DEFAULT.task)
            YamlLoader.check_task_fields(
                task_name=task_name,
                task_data=taskdata[task_name],
                declared_slots=declared_slots,
            )

    @staticmethod
    def check_task_fields(
        task_name: str,
        task_data: YamlFields.TASKS.value.STRUCTURE.value,
        declared_slots: List[str],
    ) -> None:
        """
        ensure each task contains the necessary fields and nothing more
        """
        YamlLoader.check_task_has_no_invalid_fields(
            task_name=task_name,
            data=task_data,
            valid_field_names=(
                YamlFields.TASKS.value.ACTION.value.THIS.value,
                YamlFields.TASKS.value.MEMORY.value.THIS.value,
                YamlFields.TASKS.value.FLAG.value.COMPLETE.value,
                YamlFields.TASKS.value.FLAG.value.POSSIBLE.value,
                YamlFields.TASKS.value.TRIGGER.value.THIS.value,
            ),
            field_name="",
        )
        YamlLoader.check_task_memory_field(
            task_name=task_name, task_data=task_data, declared_slots=declared_slots
        )
        YamlLoader.check_task_action_field(
            task_name=task_name, task_data=task_data, declared_slots=declared_slots
        )
        YamlLoader.check_task_trigger(
            task_name=task_name, task_data=task_data, declared_slots=declared_slots
        )
        YamlLoader.set_task_flags(task_data=task_data)

    @staticmethod
    def check_task_trigger(
        task_name: str,
        task_data: YamlFields.TASKS.value.STRUCTURE.value,
        declared_slots: List[str],
    ) -> None:
        """
        checks if the Task Trigger field has been set
        if so, check it is a valid condition with valid slots
        else set to default (no need for warning since this is not expected to be set by user)
        """
        if (
            YamlFields.TASKS.value.TRIGGER.value.THIS.value not in task_data
            or task_data[YamlFields.TASKS.value.TRIGGER.value.THIS.value] is None
        ):
            task_data[YamlFields.TASKS.value.TRIGGER.value.THIS.value] = deepcopy(
                DEFAULT.task.TriggeredBy
            )
            return

        trigger = task_data[YamlFields.TASKS.value.TRIGGER.value.THIS.value]
        if not isinstance(trigger, str):
            raise YAMLError(
                ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                    task_name=task_name,
                    field_name=YamlFields.TASKS.value.TRIGGER.value.THIS.value,
                    field_type=trigger,
                    expected_data_structure=str,
                    unexpected_data_structure=type(trigger),
                )
            )
        YamlLoader.check_all_slots_used_are_specified(
            task_name=task_name,
            declared_slots=declared_slots,
            text_with_slots=trigger,
            remembered_slots=task_data[YamlFields.TASKS.value.MEMORY.value.THIS.value],
        )
        YamlLoader.check_trigger_condition_evaluates(
            trigger=trigger,
            slot_names=declared_slots,
        )

    @staticmethod
    def check_trigger_condition_evaluates(trigger: str, slot_names: List[str]) -> None:
        """
        ensure the condition evaluates as a valid boolean expression
        (we insert fake values for each slot used in the expression - e.g. True)
        """
        trigger = trigger.replace(
            YamlFields.TASKS.value.TRIGGER.value.TASKCLASSIFIER.value, "True"
        )
        fake_slot_values = dict(
            map(lambda slot_name: (slot_name, "'some_value'"), slot_names)
        )
        trigger_with_fake_values = trigger.format(**fake_slot_values)
        try:
            eval(trigger_with_fake_values)
        except:
            raise YAMLError(
                ErrorMessages.INVALID_TRIGGER_CONDITION.value.format(
                    trigger_condition=trigger
                )
            )

    @staticmethod
    def set_task_flags(task_data: YamlFields.TASKS.value.STRUCTURE.value) -> None:
        """
        A task is complete by default
        if the task was not completed when requested, it is an open task stored in the stack
        A task is impossible if it has no actions to say or do
        """
        task_data[YamlFields.TASKS.value.FLAG.value.COMPLETE.value] = deepcopy(
            DEFAULT.task.Complete
        )
        action_data = task_data[YamlFields.TASKS.value.ACTION.value.THIS.value]
        task_data[YamlFields.TASKS.value.FLAG.value.POSSIBLE.value] = any(
            action_data[YamlFields.TASKS.value.ACTION.value.SAY.value]
        ) or any(action_data[YamlFields.TASKS.value.ACTION.value.DO.value])

    @staticmethod
    def check_task_memory_field(
        task_name: str,
        task_data: YamlFields.TASKS.value.STRUCTURE.value,
        declared_slots: List[str],
    ) -> None:
        """
        ensure task contains properly formatted memory field
        """
        if (
            YamlFields.TASKS.value.MEMORY.value.THIS.value not in task_data
            or task_data[YamlFields.TASKS.value.MEMORY.value.THIS.value] is None
        ):
            warn(
                WarningMessages.REQUIRED_FIELD_MISSING.value.format(
                    required_field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                    task_name=task_name,
                )
            )
            task_data[YamlFields.TASKS.value.MEMORY.value.THIS.value] = deepcopy(
                DEFAULT.task.Memory
            )

        YamlLoader.check_task_memory_subfields(
            task_name=task_name,
            memory_data=task_data[YamlFields.TASKS.value.MEMORY.value.THIS.value],
            declared_slots=declared_slots,
        )

    @staticmethod
    def check_task_action_field(
        task_name: str,
        task_data: YamlFields.TASKS.value.STRUCTURE.value,
        declared_slots: List[str],
    ) -> None:
        """
        ensure task contains properly formatted action field
        """
        if (
            YamlFields.TASKS.value.ACTION.value.THIS.value not in task_data
            or task_data[YamlFields.TASKS.value.ACTION.value.THIS.value] is None
        ):
            warn(
                WarningMessages.REQUIRED_FIELD_MISSING.value.format(
                    required_field_name=YamlFields.TASKS.value.ACTION.value.THIS.value,
                    task_name=task_name,
                )
            )
            task_data[YamlFields.TASKS.value.ACTION.value.THIS.value] = deepcopy(
                DEFAULT.task.Action
            )

        YamlLoader.check_task_action_subfields(
            task_name=task_name,
            action_data=task_data[YamlFields.TASKS.value.ACTION.value.THIS.value],
            declared_slots=declared_slots,
            remembered_slots=task_data[YamlFields.TASKS.value.MEMORY.value.THIS.value],
        )

    @staticmethod
    def check_task_has_no_invalid_fields(
        task_name: str,
        data: dict,
        valid_field_names: List[str],
        field_name: str,
    ) -> None:
        """
        ensure each task contains only the necessary fields
        (throws an error for any unrecognised fields)
        """
        for key in data:
            if key in valid_field_names:
                continue
            raise YAMLError(
                ErrorMessages.ADDITIONAL_FIELD_TYPE_DETECTED.value.format(
                    task_name=task_name,
                    field_name=field_name,
                    additional_field_type=key,
                    expected_field_types=valid_field_names,
                )
            )

    @staticmethod
    def check_task_action_subfields(
        task_name: str,
        action_data: YamlFields.TASKS.value.ACTION.value.STRUCTURE.value,
        declared_slots: List[str],
        remembered_slots: List[str],
    ) -> None:
        """
        ----
        Action:
            Say: List[str]
            Do: List[str]
        ----

        Ensures
            - subfields are in correct data format (dict)
            - no additional fields added by user
            - required fields included (or defaults are added)
            - values for each field are in correct format
            - all slots referenced within values have been properly declared
        """
        if not isinstance(action_data, dict):
            raise YAMLError(
                ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                    task_name=task_name,
                    field_name=YamlFields.TASKS.value.ACTION.value.THIS.value,
                    field_type="",
                    expected_data_structure=dict,
                    unexpected_data_structure=type(action_data),
                )
            )
        required_subfields = (
            YamlFields.TASKS.value.ACTION.value.SAY.value,
            YamlFields.TASKS.value.ACTION.value.DO.value,
        )
        YamlLoader.check_task_has_no_invalid_fields(
            task_name=task_name,
            data=action_data,
            valid_field_names=required_subfields,
            field_name=YamlFields.TASKS.value.ACTION.value.THIS.value,
        )
        for required_subfield in required_subfields:
            if (
                required_subfield not in action_data
                or action_data[required_subfield] is None
            ):
                warn(
                    WarningMessages.REQUIRED_FIELD_TYPE_MISSING.value.format(
                        task_name=task_name,
                        field_name=YamlFields.TASKS.value.ACTION.value.THIS.value,
                        required_field_type=required_subfield,
                    )
                )
                action_data[required_subfield] = list()

            if isinstance(action_data[required_subfield], str):
                action_data[required_subfield] = [action_data[required_subfield]]

            if not isinstance(action_data[required_subfield], list):
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=task_name,
                        field_name=required_subfield,
                        field_type="",
                        expected_data_structure=list,
                        unexpected_data_structure=type(action_data[required_subfield]),
                    )
                )
            for say_or_do in action_data[required_subfield]:
                if not isinstance(say_or_do, str):
                    raise YAMLError(
                        ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                            task_name=task_name,
                            field_name=required_subfield,
                            field_type=say_or_do,
                            expected_data_structure=str,
                            unexpected_data_structure=type(say_or_do),
                        )
                    )
                YamlLoader.check_all_slots_used_are_specified(
                    text_with_slots=say_or_do,
                    task_name=task_name,
                    declared_slots=declared_slots,
                    remembered_slots=remembered_slots,
                )
                YamlLoader.check_actions_are_valid(
                    task_name=task_name,
                    text=say_or_do,
                )

    @staticmethod
    def check_actions_are_valid(task_name: str, text: str) -> None:
        """
        if __action__ is referenced
        or action() is called
        check it is defined
        """
        function_names = list(YamlLoader.extract_all_action_references(text)) + list(
            YamlLoader.extract_action_name_from_call(text)
        )
        for function_name in function_names:
            YamlLoader.check_action_exists(
                task_name=task_name, action_name=function_name
            )

    @staticmethod
    def check_action_exists(task_name: str, action_name: str) -> None:
        """
        checks if action is listed in custom actions
        """
        try:
            eval(f"custom_actions.{action_name}")
        except:
            raise YAMLError(
                ErrorMessages.UNDEFINED_ACTION.value.format(
                    task_name=task_name, action_name=action_name
                )
            )

    @staticmethod
    def extract_all_action_references(text: str) -> Generator[str, None, None]:
        """
        any __action__ in the string is extracted
        """
        for word in text.split():
            if word.startswith("__") and word.endswith("__"):
                yield word.replace("__", "")

    @staticmethod
    def extract_action_name_from_call(text: str) -> Generator[str, None, None]:
        """
        an action() call has its name extracted and returned
        """
        if "(" in text:
            function_name, _ = text.split("(")
            yield function_name

    @staticmethod
    def check_task_memory_subfields(
        task_name: str,
        memory_data: YamlFields.TASKS.value.MEMORY.value.STRUCTURE.value,
        declared_slots: List[str],
    ) -> None:
        """
        ----
        Memory:
            Entity1:
                Scope: Local or Global
                Default: Optional[str]
                Prompt: Optional[str]
        ----

        Ensures
            - slots are in correct data format (dict)
            - all slots listed are properly declared
            - all slots listed have settings (or defaults are added)
            - for settings ensure:
                - settings are in correct data format (dict)
                - no additional fields added by user
                - required fields included (or defaults are added)
                - values for each field are in correct format
        """
        if not isinstance(memory_data, dict):
            raise YAMLError(
                ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                    task_name=task_name,
                    field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                    field_type="",
                    expected_data_structure=dict,
                    unexpected_data_structure=type(memory_data),
                )
            )

        for slot in memory_data:
            if slot not in declared_slots:
                raise YAMLError(
                    ErrorMessages.UNDEFINED_SLOT.value.format(
                        task_name=task_name,
                        slot_name=slot,
                        text_with_slot=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                    )
                )
            if memory_data[slot] is None:
                warn(
                    WarningMessages.REQUIRED_FIELD_TYPE_MISSING.value.format(
                        task_name=task_name,
                        field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                        required_field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.THIS.value,
                    )
                )
                memory_data[slot] = deepcopy(DEFAULT.slot_settings)

            if not isinstance(memory_data[slot], dict):
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=task_name,
                        field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                        field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.THIS.value,
                        expected_data_structure=dict,
                        unexpected_data_structure=type(memory_data[slot]),
                    )
                )
            YamlLoader.check_task_has_no_invalid_fields(
                task_name=task_name,
                data=memory_data[slot],
                valid_field_names=(
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value,
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value,
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value,
                ),
                field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
            )
            if (
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value
                not in memory_data[slot]
            ):
                warn(
                    WarningMessages.REQUIRED_FIELD_TYPE_MISSING.value.format(
                        task_name=task_name,
                        field_name=slot,
                        required_field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value,
                    )
                )
                memory_data[slot][
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value
                ] = deepcopy(DEFAULT.slot_settings.Default)
            slot_default = memory_data[slot][
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value
            ]
            if slot_default is not None and not isinstance(slot_default, str):
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=task_name,
                        field_name=slot,
                        field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.DEFAULT.value,
                        expected_data_structure=str,
                        unexpected_data_structure=type(slot_default),
                    )
                )

            if (
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value
                not in memory_data[slot]
            ):
                warn(
                    WarningMessages.REQUIRED_FIELD_TYPE_MISSING.value.format(
                        task_name=task_name,
                        field_name=slot,
                        required_field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value,
                    )
                )
                memory_data[slot][
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value
                ] = deepcopy(DEFAULT.slot_settings.Prompt)
            slot_prompt = memory_data[slot][
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value
            ]
            if slot_prompt is not None and not isinstance(slot_prompt, str):
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=task_name,
                        field_name=slot,
                        field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value,
                        expected_data_structure=str,
                        unexpected_data_structure=type(slot_prompt),
                    )
                )

            if (
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value
                not in memory_data[slot]
                or memory_data[slot][
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value
                ]
                is None
            ):
                warn(
                    WarningMessages.REQUIRED_FIELD_TYPE_MISSING.value.format(
                        task_name=task_name,
                        field_name=slot,
                        required_field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value,
                    )
                )
                memory_data[slot][
                    YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value
                ] = deepcopy(DEFAULT.slot_settings.Scope)
            slot_scope = memory_data[slot][
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value
            ]
            if not isinstance(slot_scope, str):
                raise YAMLError(
                    ErrorMessages.UNEXPECTED_DATA_STRUCTURE.value.format(
                        task_name=task_name,
                        field_name=slot,
                        field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value,
                        expected_data_structure=str,
                        unexpected_data_structure=type(slot_scope),
                    )
                )
            valid_scopes = (
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.LOCAL.value,
                YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.GLOBAL.value,
            )
            if slot_scope not in valid_scopes:
                raise YAMLError(
                    ErrorMessages.UNRECOGNISED_VALUE.value.format(
                        task_name=task_name,
                        field_name=slot,
                        field_type=YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.THIS.value,
                        recognised_values=valid_scopes,
                        unrecognised_value=slot_scope,
                    )
                )

    @staticmethod
    def check_task_name(task_name: str) -> None:
        """
        ensure all task names are correctly formatted
        - contains no special characters
        - upper case (throws warning only)
        """
        if not task_name.istitle():
            warn(
                WarningMessages.IMPROPER_NAME.value.format(
                    improper_name=task_name, proper_name=task_name.title()
                )
            )
        for character in task_name:
            if character not in punctuation:
                continue
            raise YAMLError(
                ErrorMessages.TEXT_CONTAINS_INVALID_CHARACTER.value.format(
                    text=task_name, invalid_character=character
                )
            )

    @staticmethod
    def extract_slots_from_string(text: str) -> Generator[str, None, None]:
        """
        extracts all slot names in a string
        e.g. `this is a {string} with {slots}`
        -> ['string', 'slots']
        """
        for _, slot, _, _ in Formatter().parse(text):
            if slot is not None:
                yield slot

    @staticmethod
    def check_all_slots_used_are_specified(
        task_name: str,
        declared_slots: List[str],
        text_with_slots: str,
        remembered_slots: YamlFields.TASKS.value.MEMORY.value.STRUCTURE.value,
    ) -> None:
        """
        ensure all slots using in templates and actions are properly declared
        """
        for slot in YamlLoader.extract_slots_from_string(text_with_slots):
            YamlLoader.check_slot_is_properly_declared(
                task_name=task_name,
                slot=slot,
                declared_slots=declared_slots,
                remembered_slots=remembered_slots,
                text=text_with_slots[:20],
            )

    @staticmethod
    def check_slot_is_properly_declared(
        task_name: str,
        declared_slots: List[str],
        slot: str,
        text: str,
        remembered_slots: YamlFields.TASKS.value.MEMORY.value.STRUCTURE.value,
    ) -> None:
        """
        any slot names used in a reply or action
        MUST be declared in the File's Slot field
        and SHOULD be declared in the Task's Memory field
        """
        if slot not in declared_slots:
            raise YAMLError(
                ErrorMessages.UNDEFINED_SLOT.value.format(
                    task_name=task_name,
                    slot_name=slot,
                    text_with_slot=text,
                )
            )
        if slot not in remembered_slots:
            warn(
                WarningMessages.UNDECLARED_SLOT.value.format(
                    task_name=task_name,
                    slot_name=slot,
                    text_with_slot=text,
                    field_name=YamlFields.TASKS.value.MEMORY.value.THIS.value,
                    type_name=YamlFields.TASKS.value.MEMORY.value.SLOT.value.SCOPE.value.LOCAL.value,
                )
            )
            remembered_slots[slot] = deepcopy(DEFAULT.slot_settings)

    @staticmethod
    def add_slot_query_tasks(data: YamlFields.STRUCTURE.value) -> None:
        """
        add tasks to allow each slot to be queried by user
        """
        for slot_name in data[YamlFields.SLOTS.value.THIS.value]:
            slot_name_with_spaces = slot_name.replace("_", " ").replace("-", " ")
            slotName = "".join(
                map(lambda word: word.title(), slot_name_with_spaces.split())
            )
            task_name = f"{YamlFields.TASKS.value.QUERY_SLOT_TYPE_TASK.value}{slotName}"
            if task_name not in data[YamlFields.TASKS.value.THIS.value]:
                data[YamlFields.TASKS.value.THIS.value][task_name] = {
                    YamlFields.TASKS.value.ACTION.value.THIS.value: {
                        YamlFields.TASKS.value.ACTION.value.SAY.value: [
                            "{" + slot_name + "}",
                            f"the {slot_name_with_spaces} is " + "{" + slot_name + "}",
                            f"is the {slot_name_with_spaces} "
                            + "{"
                            + slot_name
                            + "} ?",
                            "i think "
                            + "{"
                            + slot_name
                            + "}"
                            + f" is the {slot_name_with_spaces}",
                        ],
                    },
                    YamlFields.TASKS.value.MEMORY.value.THIS.value: {
                        slot_name: {
                            YamlFields.TASKS.value.MEMORY.value.SLOT.value.PROMPT.value: DefaultMessages.QUERY_SLOT_PROMPT.value.format(
                                slot_name=slot_name_with_spaces
                            )
                        }
                    },
                }
