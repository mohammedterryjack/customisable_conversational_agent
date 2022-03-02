from typing import Tuple

from task_tracker.core.state_tracker import StateTracker
from task_tracker.yaml_utils.datatypes import Tasks
from task_tracker.datastructures.slots import Slots
from task_tracker.datastructures.signals import Signals
from task_tracker.datastructures.stack import Stack

from oxengine import Envelope, OxService


class MANTaskPolicy(OxService):
    def __init__(self) -> None:
        path_to_settings = "task_tracker/config/settings.yml"
        self.dst = StateTracker(path_to_settings)
        # TODO - initialise OxService properly like other MANAGERS

    def forward(self, envelope: Envelope) -> Envelope:
        """
        relevant data is unpacked from the envelope
        updated (in-place) by the policy
        and repacked back into the envelope
        """
        slots, tasks = self._from_memory()
        self.dst.update(
            signals=self._from_envelope(inputs=envelope), slots=slots, tasks=tasks
        )
        self._to_memory(slots=slots, tasks=tasks)
        return envelope

    def _from_envelope(self, inputs: Envelope) -> Signals:
        """
        collects and structures all the required data from the input envelope
        as well as from the previous envelope stored in the DB
        (since we cannot store any state information in the Policy
        since different instances can be running in parallel)
        integrates state and prior_state
        """
        # TODO
        return Signals()

    def _from_memory(self) -> Tuple[Slots, Stack]:
        # TODO
        return Slots(), Stack()

    def _to_memory(self, slots: Slots, tasks: Stack) -> None:
        # TODO
        return Envelope()
