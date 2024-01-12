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
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.model = kwargs.get("model", None)

    @classmethod
    def load_model(cls, asset_name: str) -> SmileRandomForest:
        return cls(model=ee.Classifier.load(asset_name))

    def fit(
        self,
        features: ee.FeatureCollection,
        classProperty: str,
        inputProperties: list[str] | ee.List[str],
        output_mode: str = None,
    ) -> SmileRandomForest:
        output_mode = output_mode or "classification".upper()

        self.model = (
            ee.Classifier.smileRandomForest(**self.kwargs)
            .setOutputMode(output_mode)
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
