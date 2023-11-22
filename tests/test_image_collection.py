import unittest
import ee
from cnwi.cnwilib.image_collection import TimeSeries


class TimeSeriesTests(unittest.TestCase):
    def setUp(self):
        ee.Initialize()
        # Set up a sample ImageCollection for testing
        self.collection = ee.ImageCollection([ee.Image(1), ee.Image(2), ee.Image(3)])
        self.dependent = "dependent_variable"
        self.modes = 3
        self.time_series = TimeSeries(self.collection, self.dependent, self.modes)

    # def test_add_independent_single_string(self):
    #     self.time_series._add_independent("independent_variable")
    #     self.assertIn("independent_variable", self.time_series.independent)

    # def test_add_independent_list_of_strings(self):
    #     self.time_series._add_independent(
    #         ["independent_variable_1", "independent_variable_2"]
    #     )
    #     self.assertIn("independent_variable_1", self.time_series.independent)
    #     self.assertIn("independent_variable_2", self.time_series.independent)

    # def test_add_independent_invalid_input(self):
    #     with self.assertRaises(TypeError):
    #         self.time_series._add_independent(123)

    # def test_mk_freq_name(self):
    #     freq_names = self.time_series._mk_freq_name("freq")
    #     self.assertEqual(freq_names, ["freq_1", "freq_2", "freq_3"])

    def test_add_constant(self):
        self.time_series._add_constant()
        self.assertIn("constant", self.time_series.independent)

    def test_add_time(self):
        self.time_series._add_time()
        self.assertIn("t", self.time_series.independent)

    def test_add_harmonics(self):
        self.time_series._add_harmonics()
        self.assertIn("cos_1", self.time_series.independent)
        self.assertIn("sin_1", self.time_series.independent)
        self.assertIn("cos_2", self.time_series.independent)
        self.assertIn("sin_2", self.time_series.independent)
        self.assertIn("cos_3", self.time_series.independent)
        self.assertIn("sin_3", self.time_series.independent)

    def test_build(self):
        built_time_series = self.time_series.build()
        self.assertIn("constant", built_time_series.independent)
        self.assertIn("t", built_time_series.independent)
        self.assertIn("cos_1", built_time_series.independent)
        self.assertIn("sin_1", built_time_series.independent)
        self.assertIn("cos_2", built_time_series.independent)
        self.assertIn("sin_2", built_time_series.independent)
        self.assertIn("cos_3", built_time_series.independent)
        self.assertIn("sin_3", built_time_series.independent)


if __name__ == "__main__":
    unittest.main()
