from unittest import TestCase, main

from tests.utils import temporary_configuration, configuration_path, classifier_path
from task_tracker.yaml_utils.dataloader import YamlLoader
from task_tracker.core.task_policy import TaskPolicy
from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals
from task_tracker.datastructures.stack import Stack


@temporary_configuration(
    configuration="""
    Tasks: 
        Foo:
            Action:
                Say: Foo foo foo
        Bar:
            Action:
                    Say: Bar bar bar
            TriggeredBy: ({location} == 'London')
    Slots:
        location: [10]
    """,
    filename=configuration_path,
)
def settings():
    return YamlLoader.safe_load_tasks(configuration_path)


mock_settings = settings()
policy = TaskPolicy(settings=mock_settings, task_classifier_path=classifier_path)


class TestTaskPolicy(TestCase):
    def test_init(self):
        with self.subTest("settings initialised"):
            self.assertEqual(policy.settings, mock_settings)
        with self.subTest("classifier initialised"):
            self.assertIsNotNone(policy.classifier)

    def test_push_tasks_to_stack(self):
        with self.subTest("check predicted task without triggered"):
            mock_stack = Stack()
            policy.push_tasks_to_stack(
                signals=Signals(user_utterance="foo", intent=None, topic=None),
                slots=Slots(),
                tasks=mock_stack,
            )
            self.assertEqual(mock_stack.triggered, [])
            self.assertNotIn("Bar", mock_stack.open_tasks())
            self.assertEqual(mock_stack.predicted, ["Foo"])
            self.assertIn("Foo", mock_stack.open_tasks())
        with self.subTest("check triggered task overrides predicted"):
            mock_stack = Stack()
            policy.push_tasks_to_stack(
                signals=Signals(user_utterance="foo", intent=None, topic=None),
                slots=Slots(location="London"),
                tasks=mock_stack,
            )
            self.assertEqual(mock_stack.triggered, ["Bar"])
            self.assertIn("Bar", mock_stack.open_tasks())
            self.assertEqual(mock_stack.predicted, ["Foo"])
            self.assertNotIn("Foo", mock_stack.open_tasks())

    def test_update_slot_values(self):
        policy.update_slot_values(
            slots=Slots(location="Washington DC"),
            signals=Signals(user_utterance="bla", intent=None, topic=None),
            tasks=Stack(),
        )
        self.assertEqual(
            policy.settings.Tasks.Bar.Memory.location.Default, "Washington DC"
        )

    def test_select_tasks_via_model(self):
        with self.subTest("predicting using empty string doesnt throw error"):
            policy.select_tasks_via_model(
                signals=Signals(user_utterance="", intent=None, topic=None),
            )
            self.assertTrue(True)
        with self.subTest("predicting Foo Task (Easy)"):
            predicted_tasks = policy.select_tasks_via_model(
                signals=Signals(user_utterance="foo", intent=None, topic=None),
            )
            self.assertIn("Foo", predicted_tasks)
        with self.subTest("predicting Foo Task (Difficult)"):
            predicted_tasks = policy.select_tasks_via_model(
                signals=Signals(
                    user_utterance="i want to foo foo", intent=None, topic=None
                ),
            )
            self.assertIn("Foo", predicted_tasks)
        with self.subTest("predicting Bar Task"):
            predicted_tasks = policy.select_tasks_via_model(
                signals=Signals(user_utterance="bar", intent=None, topic=None),
            )
            self.assertIn("Bar", predicted_tasks)
        with self.subTest("predicting query location slot Task (Easy)"):
            predicted_tasks = policy.select_tasks_via_model(
                signals=Signals(
                    user_utterance="what's the location", intent=None, topic=None
                ),
            )
            self.assertIn("QuerySlotLocation", predicted_tasks)
        with self.subTest("predicting query location slot Task (Difficult)"):
            predicted_tasks = policy.select_tasks_via_model(
                signals=Signals(user_utterance="where to?", intent=None, topic=None),
            )
            self.assertIn("QuerySlotLocation", predicted_tasks)

    def test_get_task_data(self):
        tasks = list(policy.get_task_data(task_labels=["Foo"]))
        self.assertEqual(tasks[0], ("Foo", mock_settings.Tasks.Foo))

    def test_select_tasks_via_triggers(self):
        with self.subTest("trigger Bar task"):
            predicted_tasks = policy.select_tasks_via_triggers(
                signals=Signals(user_utterance="bla", intent=None, topic=None),
                slots=Slots(location="London"),
                tasks=Stack(),
            )
            self.assertIn("Bar", predicted_tasks)
        with self.subTest("don't trigger Bar task"):
            predicted_tasks = policy.select_tasks_via_triggers(
                signals=Signals(user_utterance="bla", intent=None, topic=None),
                slots=Slots(location="Washington DC"),
                tasks=Stack(),
            )
            self.assertNotIn("Bar", predicted_tasks)

    def test_check_task_triggers(self):
        with self.subTest("trigger Bar task"):
            predicted_tasks = policy.check_task_triggers(
                signals=Signals(user_utterance="bla", intent=None, topic=None),
                slots=Slots(location="London"),
                tasks=Stack(),
            )
            self.assertIn("Bar", predicted_tasks)
        with self.subTest("don't trigger Bar task"):
            predicted_tasks = policy.check_task_triggers(
                signals=Signals(user_utterance="bla", intent=None, topic=None),
                slots=Slots(location="Washington DC"),
                tasks=Stack(),
            )
            self.assertNotIn("Bar", predicted_tasks)

    def test_get_trigger_slots(self):
        expected_mapping = {
            "user_utterance": "'bla'",
            "intent": "'Greet'",
            "topic": "'Food'",
            "sentiment": 0.0,
            "formality": 1.0,
            "name": "'Georgie'",
            "location": "'Balham'",
            "system_utterance": None,
            "system_prompt": None,
        }
        mapping = dict(
            policy.get_trigger_slots(
                trigger_condition="bla {user_utterance} {intent} {topic} {sentiment} {formality} {name} {location} {system_utterance} {system_prompt}",
                signals=Signals(user_utterance="bla", intent="Greet", topic="Food"),
                slots=Slots(name="Georgie", location="Balham"),
                tasks=Stack(),
            )
        )
        for key, value in expected_mapping.items():
            with self.subTest(f"expected mapping key:{key}"):
                self.assertEqual(value, mapping[key])

    def test_format_slot_value(self):
        with self.subTest("does not modify non-string values"):
            result = policy.format_slot_value(slot_value=10.0)
            self.assertEqual(result, 10.0)
        with self.subTest("modifies string values"):
            result = policy.format_slot_value(slot_value="Mayor's house")
            self.assertEqual(result, "'Mayor s house'")


if __name__ == "__main__":
    main()
