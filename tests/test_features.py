import unittest
import ee
import geopandas as gpd
import pandas as pd
from cnwi.cnwilib.features import (
    insert_values_into_features,
    create_data_lookup,
    sample_regions,
)

from shapely.geometry import Point


class FeaturesTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        # Set up test data
        self.features = gpd.GeoDataFrame(
            {
                "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
                "class_name": ["class1", "class2", "class3"],
            }
        )

        self.lookup = pd.DataFrame(
            {"class_name": ["class1", "class2", "class3"], "value": [1, 2, 3]}
        )

        self.training_features = gpd.GeoDataFrame(
            {
                "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
                "class_name": ["class1", "class2", "class3"],
            }
        )

        self.testing_features = gpd.GeoDataFrame(
            {
                "geometry": [Point(0, 1), Point(1, 2), Point(2, 3)],
                "class_name": ["class1", "class2", "class3"],
            }
        )

    def test_insert_values_into_features(self):
        result = insert_values_into_features(self.features, self.lookup, "class_name")
        self.assertEqual(len(result), len(self.features))
        self.assertIn("value", result.columns)

    def test_create_data_lookup(self):
        labels = pd.Series(["class1", "class2", "class3"])
        result = create_data_lookup(labels)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(labels))
        self.assertIn("class_name", result.columns)
        self.assertIn("value", result.columns)

    def test_sample_regions(self):
        projection = ee.Projection("EPSG:4326")
        image = (
            ee.Image(list(range(1, 7)))
            .rename(["B1", "B2", "B3", "B4", "B5", "B6"])
            .reproject(projection)
        )
        features = ee.FeatureCollection(
            [
                ee.Feature(ee.Geometry.Point(0, 0), {"value": 1}),
                ee.Feature(ee.Geometry.Point(1, 1), {"value": 2}),
                ee.Feature(ee.Geometry.Point(2, 2), {"value": 3}),
            ]
        )

        samples = sample_regions(image, features, scale=1, projection=projection)

        self.assertIsInstance(samples, ee.FeatureCollection)
        self.assertEqual(samples.size().getInfo(), 3)
        self.assertEqual(samples.first().get("B1").getInfo(), 1)
