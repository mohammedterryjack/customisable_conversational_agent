from unittest import TestCase, main
from numpy import ndarray

from task_tracker.yaml_utils.dataloader import YamlLoader
from tests.utils import temporary_configuration, configuration_path
from task_tracker.datastructures.stack import Stack
from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals


@temporary_configuration(
    configuration="""
    Tasks: 
        CompleteTask:
            Action:
                Say: Bla
        IncompleteTask:
            Action:
                Say: Bla {name} {location} {event} {everMissingSlot}
            Memory:
                location:
                    Default: London
                event:
                    Default: party
    Slots:
        name: [10]
        location: [10]
        event: [10]
        everMissingSlot: [10]
    """,
    filename=configuration_path,
)
def settings():
    return YamlLoader.safe_load_tasks(configuration_path)


mock_stack = Stack()
mock_settings = settings()
mock_signals = Signals(user_utterance="bla", intent="Greet", topic="Food")


class TestStack(TestCase):
    def test_init(self):
        with self.subTest("init triggered"):
            self.assertEqual(mock_stack.triggered, [])
        with self.subTest("init predicted"):
            self.assertEqual(mock_stack.predicted, [])
        with self.subTest("init open"):
            self.assertEqual(mock_stack.open, {})
        with self.subTest("init system_utterance"):
            self.assertIsNone(mock_stack.system_utterance)
        with self.subTest("init system_prompt"):
            self.assertIsNone(mock_stack.system_prompt)

    def test_push_tasks_to_stack(self):
        mock_stack.push_tasks_to_stack(
            triggered={"CompleteTask": mock_settings.Tasks.CompleteTask},
            predicted={"IncompleteTask": mock_settings.Tasks.IncompleteTask},
        )
        with self.subTest("set triggered"):
            self.assertEqual(mock_stack.triggered, ["CompleteTask"])
        with self.subTest("set predicted"):
            self.assertEqual(mock_stack.predicted, ["IncompleteTask"])
        with self.subTest("set open"):
            self.assertIn("CompleteTask", mock_stack.open)
            self.assertIn("IncompleteTask", mock_stack.open)
        with self.subTest("set task complete flag for complete task"):
            self.assertTrue(mock_stack.open["CompleteTask"].Complete)
        with self.subTest("not set task complete flag for incomplete task"):
            self.assertFalse(mock_stack.open["IncompleteTask"].Complete)

    def test_push(self):
        mock_task = mock_settings.Tasks.IncompleteTask
        mock_task.Memory.name.Default = "Bob"
        mock_task.Memory.event.Default = "birthday"
        mock_stack.push(task_label="IncompleteTask", task_data=mock_task)
        with self.subTest("ensure same task not duplicated in stack"):
            self.assertEqual(mock_stack.open_tasks(), ["IncompleteTask"])
        with self.subTest("old slot value not overriden by None"):
            self.assertEqual(
                mock_stack.open["IncompleteTask"].Memory.location.Default, "London"
            )
        with self.subTest("None value overriden by new slot value"):
            self.assertEqual(
                mock_stack.open["IncompleteTask"].Memory.name.Default, "Bob"
            )
        with self.subTest("old slot value overriden by new slot value"):
            self.assertEqual(
                mock_stack.open["IncompleteTask"].Memory.event.Default, "birthday"
            )
        with self.subTest(
            "old slot value remains None if no new slot value to override it"
        ):
            self.assertIsNone(
                mock_stack.open["IncompleteTask"].Memory.everMissingSlot.Default
            )

    def test_pop(self):
        mock_stack.open["Foo"] = mock_settings.Tasks.CompleteTask
        mock_stack.pop()
        self.assertNotIn("Foo", mock_stack.open)

    def test_open_tasks(self):
        self.assertEqual(list(mock_stack.open), mock_stack.open_tasks())

    def test_slots_filled(self):
        with self.subTest("task with no missing slots"):
            result = mock_stack.slots_filled(
                task_memory=mock_settings.Tasks.CompleteTask.Memory
            )
            self.assertTrue(result)
        with self.subTest("task with missing slots"):
            result = mock_stack.slots_filled(
                task_memory=mock_settings.Tasks.IncompleteTask.Memory
            )
            self.assertFalse(result)


class TestSlots(TestCase):
    def test_init(self):
        mock_slots = Slots(name="Bob", location="London", time="3pm")
        with self.subTest("name init"):
            self.assertEqual(mock_slots.name, "Bob")
        with self.subTest("location init"):
            self.assertEqual(mock_slots.location, "London")
        with self.subTest("time init"):
            self.assertEqual(mock_slots.time, "3pm")


class TestSignals(TestCase):
    def test_init(self):
        with self.subTest("user utterance init"):
            self.assertEqual(mock_signals.user_utterance, "bla")
        with self.subTest("intent init"):
            self.assertEqual(mock_signals.intent, "Greet")
        with self.subTest("topic init"):
            self.assertEqual(mock_signals.topic, "Food")
        with self.subTest("sentiment init"):
            self.assertIsInstance(mock_signals.sentiment, float)
        with self.subTest("formality init"):
            self.assertIsInstance(mock_signals.formality, float)
        with self.subTest("semantics init"):
            self.assertIsInstance(mock_signals._semantics, ndarray)
        with self.subTest("syntax init"):
            self.assertIsInstance(mock_signals._syntax, ndarray)

    def test_vector(self):
        with self.subTest("check vector type"):
            self.assertIsInstance(mock_signals.vector(), ndarray)
        with self.subTest("check vector dimensions"):
            self.assertEqual(
                len(mock_signals.vector()),
                len(mock_signals._semantics) + len(mock_signals._syntax) + 2,
            )


if __name__ == "__main__":
    main()
