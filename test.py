from json import dumps

from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals
from task_tracker.datastructures.stack import Stack
from task_tracker.core.state_tracker import StateTracker

dst = StateTracker("task_tracker/config/settings.yml")
stack = Stack()
while True:
    name = input("name:")
    if not any(name):
        name = None
    dst.update(
        signals=Signals(user_utterance=input("> "), intent="Greet", topic="food"),
        slots=Slots(
            name=name,
        ),
        tasks=stack,
    )
    print(stack)
    print(dumps(stack.open, indent=2))
