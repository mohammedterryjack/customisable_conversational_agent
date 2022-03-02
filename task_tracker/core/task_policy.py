from typing import List, Generator, Tuple, Dict, Union

from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals
from task_tracker.datastructures.stack import Stack
from task_tracker.yaml_utils.datatypes import Tasks
from task_tracker.trained_models.task_classifier import TaskClassifier
from task_tracker.yaml_utils.dataloader import YamlLoader


class TaskPolicy:
    """
    selects tasks based on the classifier
    and any triggers set
    and adds tasks to open task stack
    """

    def __init__(self, settings: Tasks, task_classifier_path: str) -> None:
        self.settings = settings
        self.classifier = TaskClassifier(
            settings=self.settings, classifier_path=task_classifier_path
        )

    def push_tasks_to_stack(self, signals: Signals, slots: Slots, tasks: Stack) -> None:
        """
        updates:
            - slot values in settings
            - the current task predicted by the Policy
            - the triggered tasks according to conditions specified in settings
            - the stack with new tasks from this turn
        """
        self.update_slot_values(slots=slots, signals=signals, tasks=tasks)
        tasks.push_tasks_to_stack(
            triggered=self.select_tasks_via_triggers(
                signals=signals, slots=slots, tasks=tasks
            ),
            predicted=self.select_tasks_via_model(signals=signals),
        )

    def update_slot_values(self, slots: Slots, signals: Signals, tasks: Stack) -> None:
        """
        fills in global slot values in settings
        """
        # TODO: think about how to set Local scope slots
        for task in self.settings.Tasks.values():
            for slot_name in task.Memory:
                slot_value = (
                    getattr(slots, slot_name)
                    if hasattr(slots, slot_name)
                    else getattr(signals, slot_name)
                    if hasattr(signals, slot_name)
                    else getattr(tasks, slot_name)
                )
                if slot_value is not None:
                    task.Memory[slot_name].Default = slot_value

    def select_tasks_via_model(self, signals: Signals) -> Dict[str, Tasks]:
        """
        current tasks predicted by task classifier
        """
        task_labels = self.classifier.predict(signals.vector())
        tasks = dict(self.get_task_data(task_labels))
        return tasks

    def get_task_data(
        self, task_labels: List[str]
    ) -> Generator[Tuple[str, Tasks], None, None]:
        """
        extract the relevant task data from settings
        for the given task labels
        ignore task labels which have no behaviour defined
        (i.e. not found in the yaml file)
        """
        for task_label in task_labels:
            if task_label in self.settings.Tasks:
                yield task_label, self.settings.Tasks[task_label]

    def select_tasks_via_triggers(
        self, signals: Signals, slots: Slots, tasks: Stack
    ) -> Dict[str, Tasks]:
        """
        selects any tasks which have met their
        manually set trigger conditions
        """
        task_labels = self.check_task_triggers(
            signals=signals, slots=slots, tasks=tasks
        )
        return dict(self.get_task_data(task_labels))

    def check_task_triggers(
        self, signals: Signals, slots: Slots, tasks: Stack
    ) -> Generator[str, None, None]:
        """
        extracts all task triggers from settings
        checks if any trigger conditions are met
        if so, corresponding task label returned
        """
        for task_name, task in self.settings.Tasks.items():
            trigger_slots = dict(
                self.get_trigger_slots(
                    trigger_condition=task.TriggeredBy,
                    signals=signals,
                    slots=slots,
                    tasks=tasks,
                )
            )
            if not any(trigger_slots):
                continue
            if eval(task.TriggeredBy.format(**trigger_slots)):
                yield task_name

    @staticmethod
    def get_trigger_slots(
        trigger_condition: str, signals: Signals, slots: Slots, tasks: Tasks
    ) -> Generator[Tuple[str, str], None, None]:
        """
        extract slots from trigger condition
        fill those slots with relevant values
        from the signals, slots and tasks (if any)
        """
        for slot_name in YamlLoader.extract_slots_from_string(trigger_condition):
            if hasattr(signals, slot_name):
                slot_value = getattr(signals, slot_name)
                yield slot_name, TaskPolicy.format_slot_value(slot_value)
            elif hasattr(slots, slot_name):
                slot_value = getattr(slots, slot_name)
                yield slot_name, TaskPolicy.format_slot_value(slot_value)
            elif hasattr(tasks, slot_name):
                slot_value = getattr(tasks, slot_name)
                yield slot_name, TaskPolicy.format_slot_value(slot_value)
            else:
                yield slot_name, None

    @staticmethod
    def format_slot_value(slot_value: Union[str, float]) -> Union[str, float]:
        """
        format slot values that are strings
        to be wrapped in string quotes for proper evaluation
        """
        if not isinstance(slot_value, str):
            return slot_value
        slot_value = slot_value.replace("'", " ")
        return f"'{slot_value}'"
