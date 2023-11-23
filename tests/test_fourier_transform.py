import unittest
import ee
from cnwi.cnwilib.image_collection import TimeSeries
from cnwi.cnwilib.image_math import LinearRegression
from cnwi.fourier_transform import FourierTransform, compute_fourier_transform


class FourierTransformTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        # Set up a sample ImageCollection for testing
        self.collection = ee.ImageCollection(
            [
                ee.Image([1, 2, 3])
                .rename(["B1", "B2", "B3"])
                .set("system:time_start", 1),
                ee.Image([1, 2, 3])
                .rename(["B1", "B2", "B3"])
                .set("system:time_start", 2),
                ee.Image([1, 2, 3])
                .rename(["B1", "B2", "B3"])
                .set("system:time_start", 3),
            ]
        )
        self.dependent = "dependent_variable"
        self.modes = 3
        self.time_series = TimeSeries(self.collection, self.dependent, self.modes)
        self.trend = LinearRegression(self.time_series)

    def test_compute(self):
        fourier_transform = FourierTransform(self.time_series, self.trend)
        result = fourier_transform.compute()
        # Add assertions here to validate the result
        self.assertIsInstance(result, ee.Image)
