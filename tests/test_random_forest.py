import unittest
import ee
from cnwi.cnwilib.random_forest import SmileRandomForest, HyperParameters


class SmileRandomForestTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()

        self.projection = ee.Projection("EPSG:4326", None, 30)
        self.image = (
            ee.Image(list(range(1, 7)))
            .rename(["B1", "B2", "B3", "B4", "B5", "B6"])
            .reproject(self.projection)
        )
        self.features = ee.FeatureCollection(
            [
                ee.Feature(ee.Geometry.Point(1, 1), {"class": 0}),
                ee.Feature(ee.Geometry.Point(2, 2), {"class": 1}),
                ee.Feature(ee.Geometry.Point(3, 3), {"class": 0}),
                ee.Feature(ee.Geometry.Point(4, 4), {"class": 1}),
            ]
        )

    def test_init(self):
        # Initialize the SmileRandomForest model
        random_forest = SmileRandomForest()
        self.assertIsInstance(random_forest, SmileRandomForest)
        self.assertEqual(random_forest.output_mode, "CLASSIFICATION")
        # Assert that the model is not trained
        self.assertIsNone(random_forest.model)

    def test_fit(self):
        # sample FeatureCollection for testing
        samples = self.image.sampleRegions(
            collection=self.features, properties=["class"], scale=30
        )

        # Initialize the SmileRandomForest model
        hyper_parameters = HyperParameters(numberOfTrees=100, minLeafPopulation=2)
        random_forest = SmileRandomForest(hyper_parameters)

        # Fit the model to the sample data
        fitted_model = random_forest.fit(samples, "class", self.image.bandNames())

        # Assert that the model is trained
        self.assertIsNotNone(fitted_model.model)

        self.assertIsInstance(fitted_model.model, ee.Classifier)

    def test_predict(self):
        samples = self.image.sampleRegions(
            collection=self.features, properties=["class"], scale=30
        )

        # Initialize the SmileRandomForest model
        hyper_parameters = HyperParameters(numberOfTrees=100, minLeafPopulation=2)
        random_forest = SmileRandomForest(hyper_parameters)

        # Fit the model to the sample data
        fitted_model = random_forest.fit(samples, "class", self.image.bandNames())

        # Make predictions using the trained model
        predicted_image = random_forest.predict(self.image)

        # Assert that the predicted image is of type ee.Image
        self.assertIsInstance(predicted_image, ee.Image)


if __name__ == "__main__":
    unittest.main()
