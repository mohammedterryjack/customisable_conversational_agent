from typing import List, Generator, Tuple
from os.path import exists
from joblib import dump, load
from re import split

from numpy import ndarray
from sklearn.ensemble import RandomForestClassifier

from task_tracker.yaml_utils.datatypes import Tasks
from task_tracker.datastructures.signals import Signals
from task_tracker.yaml_utils.datatypes import TaskFields


class TaskClassifier:
    def __init__(self, settings: Tasks, classifier_path: str) -> None:

        self.model = None
        task_labels = list(settings.Tasks)

        if exists(classifier_path):
            pretrained = load(classifier_path)

            if pretrained.task_labels == task_labels:
                self.model = pretrained

        if self.model is None:
            print("training task classifier...")
            self.model = RandomForestClassifier()
            self.model.task_labels = task_labels
            self.train(settings)
            dump(self.model, classifier_path, compress=3)

    def predict(self, input_vector: ndarray) -> List[str]:
        return list(
            map(
                lambda index: self.model.task_labels[index],
                self.model.predict([input_vector]),
            )
        )

    def train(self, settings: Tasks) -> None:
        x, y = zip(*self.get_encoded_train_data(settings))
        self.model.fit(x, y)

    @staticmethod
    def get_encoded_train_data(
        settings: Tasks,
    ) -> Generator[Tuple[ndarray, ndarray], None, None]:
        """
        input = signal vector
        output = task label index
        """
        task_labels = list(settings.Tasks)
        for example_input, example_output in TaskClassifier.get_train_data(
            tasks=settings.Tasks
        ):
            yield (
                Signals(user_utterance=example_input, intent=None, topic=None).vector(),
                task_labels.index(example_output),
            )

    @staticmethod
    def get_train_data(tasks: Tasks) -> Generator[Tuple[str, str], None, None]:
        """
        training data for each task comes from
        the task name & the task response templates
        (i.e. what the system will say back to the user)
        """
        for task_name, task in tasks.items():
            for response_template in task.Action.Say:
                yield response_template, task_name
            yield TaskClassifier.convert_label_to_utterance(label=task_name), task_name

    @staticmethod
    def convert_label_to_utterance(label: str) -> str:
        """
        convert a TaskName into an example
        training utterance for the task
        e.g. DoSomeThing -> do some thing
        """
        label = label.replace(TaskFields.QUERY_SLOT_TYPE_TASK.value, "")
        label_words = split("(?=[A-Z])", label)
        return " ".join(map(lambda word: word.lower(), label_words))
