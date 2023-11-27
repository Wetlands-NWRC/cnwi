import unittest
import os
import pandas as pd
import geopandas as gpd
from cnwi.cnwilib.data import (
    get_shapefile_paths,
    create_raw_data_manifest,
    process_data_manifest,
    process_shapefile,
    create_lookup_table,
    create_processed_data_manifest,
)


class DataTests(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = "../test_data/aoi_NS/data"

    def test_get_shapefile_paths(self):
        shapefile_paths = get_shapefile_paths(self.data_dir)
        self.assertIsInstance(shapefile_paths, list)
        self.assertTrue(all(isinstance(path, str) for path in shapefile_paths))

    def test_create_raw_data_manifest(self):
        file_paths = [
            f"{self.data_dir}/122/trainingPoints.shp",
            f"{self.data_dir}/122/validationPoints.shp",
            f"{self.data_dir}/122/region.shp",
        ]
        df = create_raw_data_manifest(file_paths)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df.columns), ["file_path", "region_id", "type"])
        self.assertListEqual(df["file_path"].tolist(), file_paths)
        self.assertListEqual(df["region_id"].tolist(), ["122", "122", "122"])
        self.assertListEqual(df["type"].tolist(), [1, 2, 3])

    def test_process_data_manifest(self):
        df = pd.DataFrame(
            {
                "file_path": [
                    f"{self.data_dir}/122/trainingPoints.shp",
                    f"{self.data_dir}/122/validationPoints.shp",
                    f"{self.data_dir}/122/region.shp",
                ],
                "region_id": ["122", "122", "122"],
                "type": [1, 2, 3],
            }
        )
        gdf = process_data_manifest(df)
        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        self.assertListEqual(
            list(gdf.columns),
            [
                "class_name",
                "geometry",
                "type",
                "region_id",
            ],
        )  # Add the expected columns

    def test_process_shapefile(self):
        row = pd.Series(
            {
                "file_path": "/path/to/trainingPoints.shp",
                "region_id": "trainingPoints",
                "type": 1,
            }
        )
        gdf = process_shapefile(row)
        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        self.assertEqual(len(gdf), ...)  # Add the expected number of rows
        self.assertListEqual(
            list(gdf.columns), ["type", "region_id", ...]
        )  # Add the expected columns

    def test_create_lookup_table(self):
        df = gpd.GeoDataFrame(
            {
                "class_name": ["class1", "class2", "class3"],
                "value": [1, 2, 3],
            }
        )
        lookup_table = create_lookup_table(df, col="class_name")
        self.assertIsInstance(lookup_table, pd.DataFrame)
        self.assertEqual(len(lookup_table), 3)
        self.assertListEqual(list(lookup_table.columns), ["class_name", "value"])
        self.assertListEqual(
            lookup_table["class_name"].tolist(), ["class1", "class2", "class3"]
        )
        self.assertListEqual(lookup_table["value"].tolist(), [1, 2, 3])

    def test_create_processed_data_manifest(self):
        file_paths = ["/path/to/trainingPoints.shp", "/path/to/validationPoints.shp"]
        manifest = create_processed_data_manifest(file_paths)
        self.assertIsInstance(manifest, pd.DataFrame)
        self.assertEqual(len(manifest), ...)  # Add the expected number of rows
        self.assertListEqual(list(manifest.columns), [...])  # Add the expected columns


if __name__ == "__main__":
    unittest.main()
