import unittest
import ee
from cnwi.cnwilib.image_math import Phase, Amplitude
from cnwi.cnwilib.image_collection import TimeSeries


class PhaseTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.mode = 1
        self.phase = Phase(self.mode)

    def test_name(self):
        self.assertEqual(self.phase.name, self.mode)

    def test_set_name(self):
        new_name = "new_phase"
        self.phase.name = new_name
        self.assertEqual(self.phase.name, f"phase_{new_name}")

    def test_sin(self):
        self.assertEqual(self.phase.sin, f"sin_{self.mode}")

    def test_cos(self):
        self.assertEqual(self.phase.cos, f"cos_{self.mode}")

    def test_compute(self):
        image = ee.Image(1).cos().addBands(ee.Image(1).sin()).rename("cos_1", "sin_1")
        computed_image = self.phase.compute(image)
        self.assertIsInstance(computed_image, ee.Image)
        self.assertEqual(computed_image.bandNames().get(0).getInfo(), self.phase.name)


class AmplitudeTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.mode = 1
        self.amplitude = Amplitude(self.mode)

    def test_name(self):
        self.assertEqual(self.amplitude.name, self.mode)

    def test_set_name(self):
        new_name = "new_amplitude"
        self.amplitude.name = new_name
        self.assertEqual(self.amplitude.name, f"amp_{new_name}")

    def test_sin(self):
        self.assertEqual(self.amplitude.sin, f"sin_{self.mode}")

    def test_cos(self):
        self.assertEqual(self.amplitude.cos, f"cos_{self.mode}")

    def test_compute(self):
        image = ee.Image(1).cos().addBands(ee.Image(1).sin()).rename("cos_1", "sin_1")
        computed_image = self.amplitude.compute(image)
        self.assertIsInstance(computed_image, ee.Image)
        self.assertEqual(
            computed_image.bandNames().get(0).getInfo(), self.amplitude.name
        )


class LinearRegressionTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.time_series = TimeSeries(
            collection=ee.ImageCollection([]),
            independent=["independent"],
            dependent="dependent",
        )
        self.linear_regression = LinearRegression(self.time_series)

    def test_trend(self):
        self.assertIsInstance(self.linear_regression.trend, ee.Image)

    def test_get_coefficients(self):
        coefficients = self.linear_regression.get_coefficients()
        self.assertIsInstance(coefficients, ee.Image)
        self.assertEqual(coefficients.bandNames().get(0).getInfo(), "coef")
