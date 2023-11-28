import unittest
import os
from pathlib import Path
import geopandas as gpd
from cnwi.cnwilib.data import (
    get_shapefile_paths,
    create_raw_data_manifest,
    process_data_manifest,
    create_lookup_table,
)
from cnwi.build_features import FeatureBuilder, OpsFeatureBuilder


class FeatureBuilderTests(unittest.TestCase):
    def setUp(self):
        import os
        import pathlib as path

        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        self.data_dir = path.Path("../test_data/aoi_NS/data").absolute().resolve()
        self.builder = FeatureBuilder(self.data_dir)

    def test_init(self):
        self.assertEqual(self.builder.data_dir, Path(self.data_dir))

    def test_build_features_all(self):
        self.builder.build_features_all()


class OpsFeatureBuilderTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = "/path/to/data"
        self.builder = OpsFeatureBuilder()

    def test_build_features(self):
        # Mock the super().build_features method
        super_build_features = unittest.mock.Mock(return_value=gpd.GeoDataFrame())

        # Call the build_features method
        result = self.builder.build_features(self.data_dir)

        # Assertions
        self.assertEqual(result, super_build_features.return_value)
        super_build_features.assert_called_once_with(self.data_dir)
