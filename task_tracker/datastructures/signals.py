from typing import Optional

from numpy import ndarray, max, concatenate, zeros
from chars2vec import load_model

from conversation_metrics.models.custom_models import customise_models
from conversation_metrics.structures.utterance import Utterance

customise_models(
    measure_formality=None,
    measure_sentiment=None,
    extract_entities=None,
    vectorise=None,
)
EMBEDDING_DIMENSION = 300
syntax_model = load_model("eng_300")


class Signals:
    """
    stores annotator signals
    for task classifier to use
    """

    def __init__(
        self,
        user_utterance: str,
        intent: Optional[str],
        topic: Optional[str],
    ) -> None:
        self.user_utterance = user_utterance
        self.intent = intent
        self.topic = topic
        encoded_text = Utterance(text=user_utterance, utterance_index=0)
        self.sentiment = encoded_text.sentiment
        self.formality = encoded_text.formality
        self._semantics = (
            max(
                list(map(lambda entity: entity.semantics, encoded_text.entities)),
                axis=0,
            )
            if any(encoded_text.entities)
            else zeros(EMBEDDING_DIMENSION)
        )
        self._syntax = max(
            syntax_model.vectorize_words(user_utterance.split())
            if any(user_utterance)
            else zeros((1, EMBEDDING_DIMENSION)),
            axis=0,
        )

    def vector(self) -> ndarray:
        """
        convert signals into a vector
        """
        return concatenate(
            [[self.sentiment], [self.formality], self._semantics, self._syntax]
        )
