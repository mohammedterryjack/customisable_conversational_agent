from unittest import TestCase, main

from tests.utils import temporary_configuration, configuration_path
from task_tracker.yaml_utils.dataloader import YamlLoader
from task_tracker.core.task_compiler import TaskCompiler
from task_tracker.datastructures.stack import Stack


@temporary_configuration(
    configuration="""
    Tasks: 
        Foo:
            Action:
                Say: Bla bla bla
        Bar:
            Action:
                Do: ExampleAction(location={location})
            Memory:
                location:
                    Default: London
        IncompleteTask:
            Action:
                Say: Bla bla bla {slotX}
            Memory:
                slotX:
                    Prompt: what is slotX?
        ImpossibleTask:
    Slots:
        slotX: [10]
        location: [10]
    """,
    filename=configuration_path,
)
def settings():
    return YamlLoader.safe_load_tasks(configuration_path)


mock_settings = settings()
mock_settings.Tasks.IncompleteTask.Complete = False
mock_stack = Stack()
mock_stack.open = mock_settings.Tasks


class TestTaskCompiler(TestCase):
    def test_pop_tasks_off_stack(self):
        TaskCompiler.pop_tasks_off_stack(tasks=mock_stack)
        self.assertEqual(mock_stack.open_tasks(), ["IncompleteTask"])

    def test_get_prompts(self):
        prompts = TaskCompiler.get_prompts(open_tasks=mock_settings.Tasks)
        self.assertIn("what is slotX?", prompts)

    def test_compile_tasks(self):
        responses = TaskCompiler.compile_tasks(open_tasks=mock_settings.Tasks)
        self.assertIn("Bla bla bla", responses)

    def test_complete_task(self):
        with self.subTest("test for task with response"):
            response = TaskCompiler.complete_task(task=mock_settings.Tasks.Foo)
            self.assertEqual(response, "Bla bla bla")
        with self.subTest("test for task without response"):
            response = TaskCompiler.complete_task(task=mock_settings.Tasks.Bar)
            self.assertIsNone(response)

    def test_get_action_dictionary(self):
        action_dictionary = TaskCompiler.get_action_dictionary(
            task_actions=mock_settings.Tasks.Bar.Action.Do,
            slots={"location": "'London'"},
        )
        self.assertEqual(
            dict(action_dictionary), {"__ExampleAction__": "some generated text"}
        )

    def test_get_slot_dictionary(self):
        with self.subTest("as action parameter = False"):
            slot_dictionary = TaskCompiler.get_slot_dictionary(
                task_memory=mock_settings.Tasks.Bar.Memory, as_action_parameter=False
            )
            self.assertEqual(dict(slot_dictionary), {"location": "London"})

            slot_dictionary = TaskCompiler.get_slot_dictionary(
                task_memory=mock_settings.Tasks.IncompleteTask.Memory,
                as_action_parameter=False,
            )
            self.assertEqual(dict(slot_dictionary), {"slotX": None})

        with self.subTest("as action parameter = True"):
            slot_dictionary = TaskCompiler.get_slot_dictionary(
                task_memory=mock_settings.Tasks.Bar.Memory, as_action_parameter=True
            )
            self.assertEqual(dict(slot_dictionary), {"location": "'London'"})

            slot_dictionary = TaskCompiler.get_slot_dictionary(
                task_memory=mock_settings.Tasks.IncompleteTask.Memory,
                as_action_parameter=True,
            )
            self.assertEqual(dict(slot_dictionary), {"slotX": "'None'"})

    def test_fill_response_template(self):
        filled_template = TaskCompiler.fill_response_template(
            response_template="bla bla {location} bla bla __ExampleAction__ bla bla",
            slot_dictionary={"location": "London"},
            action_dictionary={"__ExampleAction__": "some generated text"},
        )
        self.assertEqual(
            filled_template, "bla bla London bla bla some generated text bla bla"
        )

    def test_impossible_task(self):
        response = TaskCompiler.impossible_task(task_label="Foo")
        self.assertIn("foo", response.split())


if __name__ == "__main__":
    main()
