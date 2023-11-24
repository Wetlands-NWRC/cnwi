import unittest
import ee
from cnwi.cnwilib.image import *


class ImageStackTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.image1 = ee.Image(1)
        self.image2 = ee.Image(2)
        self.image3 = ee.Image(3)
        self.stack = ImageStack()

    def test_add(self):
        self.stack.add(self.image1)
        self.assertEqual(len(self.stack), 1)
        self.stack.add(self.image2)
        self.assertEqual(len(self.stack), 2)
        self.stack.add(self.image3)
        self.assertEqual(len(self.stack), 3)

    def test_stack(self):
        self.stack.add(self.image1)
        self.stack.add(self.image2)
        self.stack.add(self.image3)
        stacked_image = self.stack.stack()
        self.assertIsInstance(stacked_image, ee.Image)
        # Add assertions here to validate the stacked_image


class ImageBuilderTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.image = ee.Image(list(range(1, 7))).rename(
            ["B1", "B2", "B3", "B4", "B5", "B6"]
        )
        self.builder = ImageBuilder()

    def test_add_ndvi(self):
        calculator = NDVICalculator(nir="B5", red="B4", name="NDVI")
        self.builder.image = self.image
        self.builder.add_calculator(calculator)
        self.assertIsInstance(self.builder.image, ee.Image)
        self.assertEqual(
            self.builder.image.bandNames().getInfo(),
            ["B1", "B2", "B3", "B4", "B5", "B6", "NDVI"],
        )
        # Add assertions here to validate the image after adding NDVI

    def test_add_savi(self):
        calculator = SAVICalculator(nir="B5", red="B4", name="SAVI")
        self.builder.image = self.image
        self.builder.add_calculator(calculator)
        self.assertIsInstance(self.builder.image, ee.Image)
        # Add assertions here to validate the image after adding SAVI
        self.assertEqual(
            self.builder.image.bandNames().getInfo(),
            ["B1", "B2", "B3", "B4", "B5", "B6", "SAVI"],
        )

    def test_add_tasseled_cap(self):
        calculator = TasseledCapCalculator(
            **{
                "blue": "B1",
                "green": "B2",
                "red": "B3",
                "nir": "B4",
                "swir1": "B5",
                "swir2": "B6",
            }
        )
        self.builder.image = self.image
        self.builder.add_calculator(calculator)
        self.assertIsInstance(self.builder.image, ee.Image)
        # Add assertions here to validate the image after adding Tasseled Cap
        self.assertEqual(
            self.builder.image.bandNames().getInfo(),
            ["B1", "B2", "B3", "B4", "B5", "B6", "brightness", "greenness", "wetness"],
        )

    def test_add_ratio(self):
        calculator = RatioCalculator(numerator="B5", denominator="B4", name="Ratio")
        self.builder.image = self.image
        self.builder.add_calculator(calculator)
        self.assertIsInstance(self.builder.image, ee.Image)
        # Add assertions here to validate the image after adding Ratio
        self.assertEqual(
            self.builder.image.bandNames().getInfo(),
            ["B1", "B2", "B3", "B4", "B5", "B6", "Ratio"],
        )

    def test_select_dv(self):
        self.builder.image = ee.Image(list(range(1, 4))).rename(["VV", "VH", "angle"])
        result = self.builder.select_dv()
        self.assertIsInstance(result, ImageBuilder)
        self.assertEqual(
            result.image.bandNames().getInfo(),
            ["VV", "VH"],
        )

    def test_select_dh(self):
        self.builder.image = ee.Image(list(range(1, 4))).rename(["HH", "HV", "angle"])
        result = self.builder.select_dh()
        self.assertIsInstance(result, ImageBuilder)
        self.assertEqual(
            result.image.bandNames().getInfo(),
            ["HH", "HV"],
        )

    def test_select_data_cube_bands(self):
        from band_names import data_cube_band_names, expected

        image = ee.Image(list(range(1, len(data_cube_band_names) + 1))).rename(
            data_cube_band_names
        )

        self.builder.image = image
        result = self.builder.select_data_cube_bands()
        self.assertIsInstance(result, ImageBuilder)
        self.assertEqual(
            result.image.bandNames().getInfo(),
            expected,
        )

    def test_add_box_car(self):
        radius = 1
        self.builder.image = self.image
        self.builder.add_box_car(radius)
        self.assertIsInstance(self.builder.image, ee.Image)
        # Add assertions here to validate the image after adding Box Car

    def test_build(self):
        self.builder.image = self.image
        result = self.builder.build()
        self.assertIsInstance(result, ImageBuilder)
        self.assertEqual(result.image, self.image)


class ImageDirectorTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        self.builder = ImageBuilder()
        self.director = ImageDirector(self.builder)

    def test_build_data_cube(self):
        from band_names import data_cube_band_names, expected, expected_calc_res

        image = ee.Image(list(range(1, len(data_cube_band_names) + 1))).rename(
            data_cube_band_names
        )
        expected.extend(expected_calc_res)

        result = self.director.build_data_cube(image)
        self.assertIsInstance(result, ImageBuilder)
        self.assertIsInstance(result.image, ee.Image)
        self.assertEqual(result.image.bandNames().getInfo(), expected)
        # Add assertions here to validate the result

    def test_build_land_sat_8(self):
        image = ee.Image()
        with self.assertRaises(NotImplementedError):
            self.director.build_land_sat_8(image)

    def test_build_sentinel_1(self):
        image = ee.Image()
        result = self.director.build_sentinel_1(image)
        self.assertIsInstance(result, ImageBuilder)
        # Add assertions here to validate the result

    def test_build_alos(self):
        image = ee.Image()
        result = self.director.build_alos(image)
        self.assertIsInstance(result, ImageBuilder)
        # Add assertions here to validate the result
