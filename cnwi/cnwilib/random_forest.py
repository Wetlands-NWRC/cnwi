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
        self.model = None

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

    def fit(
        self,
        features: ee.FeatureCollection,
        classProperty: str,
        inputProperties: list[str] | ee.List[str],
    ) -> SmileRandomForest:
        self.model = (
            ee.Classifier.smileRandomForest(**self.params.__dict__)
            .setOutputMode(self.output_mode)
            .train(features, classProperty, inputProperties)
        )
        return self

    def predict(
        self, X: ee.Image | ee.FeatureCollection
    ) -> ee.Image | ee.FeatureCollection:
        return X.classify(self.model)

    def save_model(self, asset_name) -> ee.batch.Task:
        return ee.batch.Export.classifier.toAsset(
            classifier=self.model, assetId=asset_name
        )

    def load_model(self, asset_name: str) -> SmileRandomForest:
        self.model = ee.Classifier.load(asset_name)
        return self
