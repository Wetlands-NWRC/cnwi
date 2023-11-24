from __future__ import annotations
from dataclasses import dataclass

import ee


@dataclass
class HyperParameters:
    """Hyper parameters for the random forest model"""

    numberOfTrees: int = 1000
    variablesPerSplit: int = None
    minLeafPopulation: int = 1
    bagFraction: float = 0.5
    maxNodes: int = None
    seed: int = 0


class SmileRandomForest:
    def __init__(
        self,
        hyper_paramaters: HyperParameters = HyperParameters(),
        output_mode: str = None,
    ) -> None:
        self.params = hyper_paramaters
        self.output_mode = output_mode
        self._model = None

    @property
    def output_mode(self) -> str:
        return self._output_mode

    @output_mode.setter
    def output_mode(self, mode: str) -> None:
        if mode is None:
            mode = "classification".upper()

        if mode not in ["CLASSIFICATION", "MULTIPROBABILITY"]:
            raise ValueError(
                "mode must be one of 'classification', or 'multi_probability'"
            )
        self._output_mode = mode

    @property
    def model(self) -> ee.Classifier:
        return self._model

    def fit(
        self,
        features: ee.FeatureCollection,
        classProperty: str,
        inputProperties: list[str] | ee.List[str],
    ) -> SmileRandomForest:
        self._model = (
            ee.Classifier.smileRandomForest(**self.params.__dict__)
            .setOutputMode(self.output_mode)
            .train(features, classProperty, inputProperties)
        )
        return self

    def predict(self, image: ee.Image) -> ee.Image:
        return image.classify(self._model)
