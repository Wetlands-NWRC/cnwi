import unittest
import ee
from cnwi.rsd import RemoteSensingDatasetProcessor


class RemoteSensingDatasetProcessorTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        # Set up a sample ImageCollection for testing
        base_image = ee.Image([_ for _ in range(1, 7)]).rename(
            [f"B_{x}" for x in range(1, 7)]
        )
        self.collection = ee.ImageCollection([base_image for _ in range(1, 4)])
        self.processor = RemoteSensingDatasetProcessor(self.collection)

    def test_filter_dates(self):
        start_date = "2022-01-01"
        end_date = "2022-01-31"
        filtered_dataset = self.processor.filter_dates(start_date, end_date).build()
        # Assert that the filtered dataset has the expected number of images
        self.assertEqual(filtered_dataset.size().getInfo(), 3)

    def test_filter_bounds(self):
        # Create a sample geometry
        geom = ee.Geometry.Point(0, 0)
        filtered_dataset = self.processor.filter_bounds(geom).build()
        # Assert that the filtered dataset has the expected number of images
        self.assertEqual(filtered_dataset.size().getInfo(), 3)

    def test_select(self):
        selected_dataset = self.processor.select("B_.*").build()
        # Assert that the selected dataset has the expected number of bands
        self.assertEqual(selected_dataset.first().bandNames().size().getInfo(), 6)

    def test_add_box_car(self):
        radius = 3
        processed_dataset = self.processor.add_box_car(radius).build()
        # Assert that the processed dataset has the expected number of images
        self.assertEqual(processed_dataset.size().getInfo(), 3)

    def test_add_ratio(self):
        band1 = "B_1"
        band2 = "B_2"
        processed_dataset = self.processor.add_ratio(band1, band2).build()
        # Assert that the processed dataset has the expected number of bands
        self.assertEqual(processed_dataset.first().bandNames().size().getInfo(), 7)

    def test_add_ndvi(self):
        nir_band = "B_1"
        red_band = "B_2"
        processed_dataset = self.processor.add_ndvi(nir_band, red_band).build()
        # Assert that the processed dataset has the expected number of bands
        self.assertEqual(processed_dataset.first().bandNames().size().getInfo(), 7)

    def test_add_savi(self):
        nir_band = "B_1"
        red_band = "B_2"
        processed_dataset = self.processor.add_savi(nir_band, red_band).build()
        # Assert that the processed dataset has the expected number of bands
        self.assertEqual(processed_dataset.first().bandNames().size().getInfo(), 7)

    def test_add_tasseled_cap(self):
        blue_band = "B_1"
        green_band = "B_2"
        red_band = "B_3"
        nir_band = "B_4"
        swir1_band = "B_5"
        swir2_band = "B_6"
        processed_dataset = self.processor.add_tasseled_cap(
            blue_band, green_band, red_band, nir_band, swir1_band, swir2_band
        ).build()
        # Assert that the processed dataset has the expected number of bands
        self.assertEqual(processed_dataset.first().bandNames().size().getInfo(), 9)
