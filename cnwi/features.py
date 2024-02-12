import ee


class Features:
    def __init__(self, asset_id, label_col: str = None) -> None:
        self.dataset = asset_id
        self.label_col = label_col or "class_name"

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, args):
        self._dataset = ee.FeatureCollection(args)

    def extract(self, image):
        samples = image.sampleRegions(
            collection=self._dataset, scale=10, tileScale=16, geometries=True
        )
        return Features(samples, label_col=self.label_col)

    def get_training(self):
        features = self._dataset.filter(ee.Filter.eq("split", "train"))
        return Features(features, label_col=self.label_col)

    def get_testing(self):
        test = self._dataset.filter(ee.Filter.eq("split", "test"))
        return Features(test, label_col=self.label_col)

    def save_to_asset(self, asset_id, start_task: bool = True) -> ee.batch.Task:
        task = ee.batch.Export.table.toAsset(
            collection=self._dataset, assetId=asset_id, description=""
        )

        if start_task:
            task.start()

        return task
