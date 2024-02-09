import unittest
import ee
from cnwi.rsd import RemoteSensingDatasetProcessor


class TestSmileRandomForest(unittest.TestCase):
    def setUp(self) -> None:
        ee.Initialize()
        features = ee.FeatureCollection()

        return super().setUp()

    def test_fit(self):
        pass
