from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals
from task_tracker.datastructures.stack import Stack
from task_tracker.core.task_policy import TaskPolicy
from task_tracker.core.task_compiler import TaskCompiler
from task_tracker.yaml_utils.dataloader import YamlLoader
from task_tracker.yaml_utils.datatypes import Tasks


class StateTracker:
    """
    Keeps track of the current state of the dialogue
    updates relevant information
    and selects the current task
    """

    def __init__(
        self,
        settings_filename: str,
        task_classifier_path: str = "task_tracker/trained_models/random_forest.joblib",
    ) -> None:
        settings = YamlLoader.safe_load_tasks(settings_filename)
        self.selector = TaskPolicy(
            settings=settings, task_classifier_path=task_classifier_path
        )
        self.compilor = TaskCompiler()

    def update(self, signals: Signals, slots: Slots, tasks: Stack) -> None:
        """
        dialogue_state is updated in-place
        1) TaskClassifier: predicts and adds the current task to open tasks stack
        2) TaskCompiler: executes completed tasks from the open tasks stack
        """
        self.selector.push_tasks_to_stack(
            signals=signals,
            slots=slots,
            tasks=tasks,
        )
        self.compilor.pop_tasks_off_stack(tasks=tasks)
