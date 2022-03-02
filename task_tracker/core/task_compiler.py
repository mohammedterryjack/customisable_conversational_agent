from typing import Dict, Tuple, Generator, Optional
from random import choice

from task_tracker.datastructures.stack import Stack
from task_tracker.yaml_utils.datatypes import Tasks
from task_tracker.yaml_utils.dataloader import YamlLoader
from task_tracker.yaml_utils.messages import DefaultMessages
from task_tracker.config.custom_actions import *


class TaskCompiler:
    """
    attempts to execute open task in the stack
    """

    @staticmethod
    def pop_tasks_off_stack(tasks: Stack) -> None:
        tasks.system_utterance = "\n".join(
            TaskCompiler.compile_tasks(open_tasks=tasks.open)
        )
        prompts = list(TaskCompiler.get_prompts(open_tasks=tasks.open))
        tasks.system_prompt = choice(prompts) if any(prompts) else None
        tasks.pop()

    @staticmethod
    def get_prompts(open_tasks: Tasks) -> Generator[str, None, None]:
        """
        take any prompts from incomplete tasks
        only from slots which haven't been filled yet
        (to encourage the user to provide the necessary
        slot information for their completion)
        """
        for task in open_tasks.values():
            if not task.Complete:
                for slot in task.Memory.values():
                    if slot.Default is None and slot.Prompt is not None:
                        yield slot.Prompt

    @staticmethod
    def compile_tasks(open_tasks: Tasks) -> Generator[str, None, None]:
        """
        for each open task in the stack
        - complete tasks:
            get template replies (if applicable)
        """
        for task_name, task in open_tasks.items():
            if not task.Possible:
                yield TaskCompiler.impossible_task(task_name)
                continue
            if task.Complete:
                response = TaskCompiler.complete_task(task)
                if response is None:
                    continue
                yield response

    @staticmethod
    def complete_task(task: Tasks) -> Optional[str]:
        """
        execute all tasks
        return a response (if any)
        """
        slot_dictionary = dict(
            TaskCompiler.get_slot_dictionary(
                task_memory=task.Memory, as_action_parameter=True
            )
        )
        action_dictionary = dict(
            TaskCompiler.get_action_dictionary(
                task_actions=task.Action.Do, slots=slot_dictionary
            )
        )
        if any(task.Action.Say):
            slot_dictionary = dict(
                TaskCompiler.get_slot_dictionary(
                    task_memory=task.Memory,
                )
            )
            return TaskCompiler.fill_response_template(
                response_template=choice(task.Action.Say),
                slot_dictionary=slot_dictionary,
                action_dictionary=action_dictionary,
            )

    @staticmethod
    def get_action_dictionary(
        task_actions: Tasks, slots: Dict[str, str]
    ) -> Generator[Tuple[str, str], None, None]:
        """
        a generator to return of all custom actions in a task and their computed result
        fills in action slots and evaluates it to get results
        returns action_name,action_result
        """
        for custom_action in task_actions:
            action_name = list(YamlLoader.extract_action_name_from_call(custom_action))[
                0
            ]
            action_result = eval(custom_action.format(**slots))
            yield f"__{action_name}__", action_result

    @staticmethod
    def get_slot_dictionary(
        task_memory: Tasks, as_action_parameter: bool = False
    ) -> Generator[Tuple[str, str], None, None]:
        """
        a generator to return all slots in a task
        returns slot_name,slot_value
        """
        for slot_name, slot_data in task_memory.items():
            slot_value = slot_data.Default
            if as_action_parameter:
                slot_value = f"'{slot_value}'"
            yield slot_name, slot_value

    @staticmethod
    def fill_response_template(
        response_template: str,
        slot_dictionary: Dict[str, str],
        action_dictionary: Dict[str, str],
    ) -> str:
        """
        fill in all slots and action references
        """
        for action_name, action_result in action_dictionary.items():
            response_template = response_template.replace(action_name, action_result)
        return response_template.format(**slot_dictionary)

    @staticmethod
    def impossible_task(task_label: str) -> str:
        """
        respond with one of the default replies
        """
        response_template = choice(DefaultMessages.IMPOSSIBLE_TASK.value)
        return response_template.format(task_name=task_label.lower())
