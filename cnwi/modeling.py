from __future__ import annotations
from dataclasses import dataclass

import ee


class ConfusionMatrix:
    def __init__(self, data):
        self.cfm = data
        self.data = [ee.Feature(None, {"matrix": self.cfm.array()})]

    def add_accuracy(self):
        self.data.append(ee.Feature(None, {"overall": self.cfm.accuracy()}))
        return self

    def add_producers(self):
        self.data.append(
            ee.Feature(
                None, {"producers": self.cfm.producersAccuracy().toList().flatten()}
            )
        )
        return self

    def add_consumers(self):
        self.data.append(
            ee.Feature(
                None, {"consumers": self.cfm.consumersAccuracy().toList().flatten()}
            )
        )
        return self

    def add_order(self):
        self.data.append(ee.Feature(None, {"order": self.cfm.order()}))
        return self

    def get_compoents(self):
        components = [
            ee.Feature(None, {"matrix": self.cfm.array()}),
            ee.Feature(None, {"overall": self.cfm.accuracy()}),
            ee.Feature(
                None, {"producers": self.cfm.producersAccuracy().toList().flatten()}
            ),
            ee.Feature(
                None, {"consumers": self.cfm.consumersAccuracy().toList().flatten()}
            ),
            ee.Feature(None, {"order": self.cfm.order}),
        ]
        self.cfm = ee.FeatureCollection(components)
        return self

    def save_table_to_drive(self, name, folder_name, start_task: bool = True):
        task = ee.batch.Export.table.toDrive(
            collection=self.cfm,
            description="",
            folder=folder_name,
            fileNamePrefix=name,
            fileFormat="GeoJSON",
        )

        if start_task:
            task.start()
        return task


@dataclass
class HyperParameters:
    """Hyper parameters for the random forest model"""

    numberOfTrees: int = 1000
    variablesPerSplit: int = None
    minLeafPopulation: int = 1
    bagFraction: float = 0.5
    maxNodes: int = None
    seed: int = 0

    def __call__(self):
        return HyperParameters()


class SmileRandomForest:
    def __init__(self, hyperparams: HyperParameters = HyperParameters()) -> None:
        self.hyper = hyperparams
        self._model = None

    @classmethod
    def load_model(cls, asset_name: str) -> SmileRandomForest:
        instance = cls()
        instance.model = ee.Classifier.load(asset_name)
        return instance

    def fit(
        self,
        features: ee.FeatureCollection,
        label_col: str,
        predictors: list[str] | ee.List[str],
    ) -> SmileRandomForest:

        self.model = ee.Classifier.smileRandomForest(
            numberOfTrees=self.hyper.numberOfTrees,
            variablesPerSplit=self.hyper.variablesPerSplit,
            minLeafPopulation=self.hyper.minLeafPopulation,
            bagFraction=self.hyper.bagFraction,
            maxNodes=self.hyper.maxNodes,
            seed=self.hyper.seed,
        ).train(features, label_col, predictors)
        return self

    def predict(
        self, X: ee.Image | ee.FeatureCollection
    ) -> ee.Image | ee.FeatureCollection:
        return X.classify(self.model)

    def assess(self, obj) -> ConfusionMatrix:
        if isinstance(obj, ee.FeatureCollection):
            # compute error matrix
            predict = self.predict(obj)
            order = obj.aggregate_array("class_name").distinct()
            matrix = predict.errorMatrix("class_name", "classification", order)
            return ConfusionMatrix(data=matrix)
        else:
            return None

    def save_model(self, asset_name) -> ee.batch.Task:
        task = ee.batch.Export.classifier.toAsset(
            classifier=self.model, assetId=asset_name
        )

        task.start()

        return task
