from typing import Dict, Optional, Generator, Tuple, List

from task_tracker.yaml_utils.datatypes import Tasks


class Stack:
    """
    stores tasks
    in a stack
    """

    def __init__(self, open_tasks: Optional[Dict[str, Tasks]] = None) -> None:
        self.triggered: List[str] = list()
        self.predicted: List[str] = list()
        self.open = dict() if open_tasks is None else open_tasks
        self.system_utterance: Optional[str] = None
        self.system_prompt: Optional[str] = None

    def __repr__(self) -> str:
        return f"""
        Stack:
            triggered: {self.triggered}
            predicted: {self.predicted}
            open: {self.open_tasks()}
            response: {self.system_utterance}
            prompt: {self.system_prompt}
        """

    def push_tasks_to_stack(
        self, triggered: Dict[str, Tasks], predicted: Dict[str, Tasks]
    ) -> None:
        """
        adds each new task into stack
        checks which tasks are now complete
        (triggered tasks override predicted)
        """
        self.predicted = list(predicted)
        self.triggered = list(triggered)
        selected_tasks = triggered if any(triggered) else predicted
        for task_name, task_data in selected_tasks.items():
            self.push(task_label=task_name, task_data=task_data)
        for task in self.open.values():
            task.Complete = self.slots_filled(task_memory=task.Memory)

    def push(self, task_label: str, task_data: Tasks) -> None:
        """
        if the same task already exists in open stack,
        copy across its slot values
        (without overriding more current values)
        """
        existing_task_data = self.open.get(task_label)
        if existing_task_data is not None:
            for slot_name, slot_value in task_data.Memory.items():
                if slot_value.Default is None:
                    slot_value.Default = existing_task_data.Memory[slot_name].Default
        self.open[task_label] = task_data

    def pop(self) -> None:
        """
        remove the task from open tasks
        which are impossible or complete
        """
        self.open = dict(self.filter_tasks())

    def filter_tasks(self) -> Generator[Tuple[str, str], None, None]:
        for task_name, task in self.open.items():
            if not task.Complete and task.Possible:
                yield task_name, task

    def open_tasks(self) -> List[str]:
        return list(self.open)

    @staticmethod
    def slots_filled(task_memory: Tasks) -> bool:
        """
        all slots in task Memory have a value
        """
        for slot in task_memory.values():
            if slot.Default is None:
                return False
        return True
