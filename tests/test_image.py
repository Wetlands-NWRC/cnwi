import unittest
import ee
from cnwi.cnwilib.image import ImageStack


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
