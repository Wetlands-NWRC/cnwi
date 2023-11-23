import unittest
import ee
from cnwi.cnwilib.image_collection import TimeSeries
from cnwi.cnwilib.image_math import LinearRegression
from cnwi.fourier_transform import FourierTransform, compute_fourier_transform


# cloud mask function
def mask_l8_sr(image: ee.Image):
    """Masks clouds in Landsat 8 SR image."""
    qa_mask = image.select("QA_PIXEL").bitwiseAnd(2**4).eq(0)
    saturation_mask = image.select("QA_RADSAT").eq(0)

    # Apply the scaling factors to the appropriate bands.
    optical_bands = image.select("SR_B.*").multiply(0.0000275).add(-0.2)
    thermal_bands = image.select("ST_B.*").multiply(0.00341802).add(149.0)

    # Replace the original bands with the scaled ones and apply the masks.
    return (
        image.addBands(optical_bands, None, True)
        .addBands(thermal_bands, None, True)
        .updateMask(qa_mask)
        .updateMask(saturation_mask)
    )


class FourierTransformTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        # Set up a sample ImageCollection for testing
        self.collection = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterDate("2013", "2022")
            .filterBounds(ee.Geometry.Point(-77.17593890457817, 44.095224852158104))
            .map(mask_l8_sr)
        )
        self.dependent = "SR_B5"
        self.modes = 3
        self.time_series = TimeSeries(
            self.collection, self.dependent, self.modes
        ).build()
        self.trend = LinearRegression(self.time_series)

    def test_compute(self):
        fourier_transform = FourierTransform(self.time_series, self.trend)
        result = fourier_transform.compute()
        # Add assertions here to validate the result
        self.assertIsInstance(result, ee.Image)
