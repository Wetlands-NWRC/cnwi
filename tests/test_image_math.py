import unittest
import ee
from cnwi.cnwilib.image_math import *
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
        self.time_series = TimeSeries(
            collection=self.collection,
            dependent="B3",
        ).build()
        self.linear_regression = LinearRegression(self.time_series)

    def test_trend(self):
        self.assertIsInstance(self.linear_regression.trend, ee.Image)

    def test_get_coefficients(self):
        coefficients = self.linear_regression.get_coefficients()
        self.assertIsInstance(coefficients, ee.Image)
        self.assertEqual(coefficients.bandNames().get(0).getInfo(), "constant_coef")


class NDVICalculatorTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.nir_band = "B4"
        self.red_band = "B3"
        self.calculator = NDVICalculator(self.nir_band, self.red_band)

    def test_init(self):
        self.assertEqual(self.calculator.nir, self.nir_band)
        self.assertEqual(self.calculator.red, self.red_band)
        self.assertEqual(self.calculator.name, "NDVI")

    def test_init_with_custom_name(self):
        custom_name = "CustomNDVI"
        calculator = NDVICalculator(self.nir_band, self.red_band, name=custom_name)
        self.assertEqual(calculator.name, custom_name)

    def test_compute(self):
        image = ee.Image([0.1, 0.2, 0.3, 0.4]).rename(["B1", "B2", "B3", "B4"])
        computed_image = self.calculator.compute(image)
        self.assertIsInstance(computed_image, ee.Image)
        self.assertEqual(
            computed_image.bandNames().get(0).getInfo(), self.calculator.name
        )


class SAVICalculatorTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.nir_band = "B4"
        self.red_band = "B3"
        self.calculator = SAVICalculator(self.nir_band, self.red_band)

    def test_init(self):
        self.assertEqual(self.calculator.nir, self.nir_band)
        self.assertEqual(self.calculator.red, self.red_band)
        self.assertEqual(self.calculator.name, "SAVI")

    def test_init_with_custom_name(self):
        custom_name = "CustomSAVI"
        calculator = SAVICalculator(self.nir_band, self.red_band, name=custom_name)
        self.assertEqual(calculator.name, custom_name)

    def test_compute(self):
        image = ee.Image([0.1, 0.2, 0.3, 0.4]).rename(["B1", "B2", "B3", "B4"])
        computed_image = self.calculator.compute(image)
        self.assertIsInstance(computed_image, ee.Image)
        self.assertEqual(
            computed_image.bandNames().get(0).getInfo(), self.calculator.name
        )


class RatioCalculatorTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.numerator_band = "B4"
        self.denominator_band = "B3"
        self.calculator = RatioCalculator(self.numerator_band, self.denominator_band)

    def test_init(self):
        self.assertEqual(self.calculator.numerator, self.numerator_band)
        self.assertEqual(self.calculator.denominator, self.denominator_band)
        self.assertEqual(self.calculator.name, "Ratio")

    def test_init_with_custom_name(self):
        custom_name = "CustomRatio"
        calculator = RatioCalculator(
            self.numerator_band, self.denominator_band, name=custom_name
        )
        self.assertEqual(calculator.name, custom_name)

    def test_compute(self):
        image = ee.Image([0.1, 0.2, 0.3, 0.4]).rename(["B1", "B2", "B3", "B4"])
        computed_image = self.calculator.compute(image)
        self.assertIsInstance(computed_image, ee.Image)
        self.assertEqual(
            computed_image.bandNames().get(0).getInfo(), self.calculator.name
        )
