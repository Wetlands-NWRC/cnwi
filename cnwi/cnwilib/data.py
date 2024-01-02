from __future__ import annotations

import os

from typing import Iterable, Tuple

import ee
import geopandas as gpd
import pandas as pd


####################################################################################################
# Client Side Functions and Classes
class Manifest:
    """Class representing a manifest of data files."""

    M = {
        "trainingPoints": 1,
        "validationPoints": 2,
        "region": 3,
    }

    def __init__(self, data_dir: str) -> None:
        """
        Initialize the Data class.

        Args:
            data_dir (str): The directory path where the data is located.
        """
        self.data_dir = data_dir
        self.manifest = None
        self.groupby_col = "region_id"

    def __iter__(self) -> Iterable[Tuple[str, pd.DataFrame]]:
        """Iterates over the manifest, yielding region IDs and corresponding dataframes."""
        for idx, df in self.manifest.groupby(self.groupby_col):
            yield idx, df

    def get_file_paths(self) -> Manifest:
        """gets files from a directory"""
        shapefile_paths = []
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".shp"):
                    shapefile_paths.append(os.path.join(root, file))

        self.manifest = pd.DataFrame(shapefile_paths, columns=["file_path"])
        return self

    def set_region_id(self) -> Manifest:
        """sets the region id"""
        self.manifest["region_id"] = self.manifest["file_path"].str.extract(
            r"(\b\d{1,3}\b)"
        )
        return self

    def extract_type(self) -> Manifest:
        """sets the type"""
        self.manifest["type"] = self.manifest["file_path"].str.extract(
            r"/(\w+)(?:Points)?\.shp"
        )
        return self

    def set_type_int(self) -> Manifest:
        """sets the type"""
        self.manifest["type"] = self.manifest["type"].replace(self.M)
        return self

    def create(self) -> Manifest:
        """creates the manifest"""
        self.get_file_paths().set_region_id().extract_type().set_type_int()
        self.manifest = self.manifest.sort_values(by=["region_id", "type"]).reset_index(
            drop=True
        )
        return self

    def save(self, where: str) -> Manifest:
        """Save the manifest to a csv file.

        Args:
            where (str): The path to save the csv file.

        Returns:
            Manifest: The Manifest instance.
        """
        self.manifest.to_csv(where, index=False)
        return self


class ManifestProcessor:
    def __init__(self, manifest: Manifest) -> None:
        self.manifest = manifest
        self.label_col = "class_name"
        self.training = []
        self.regions = []

    def read_manifest(self) -> ManifestProcessor:
        """on read manifest,
        1) load the shapefiles into a geopandas dataframe
        2) add the type column to the dataframe
        3) add the region_id column to the dataframe
        """
        for _, group in self.manifest:
            for _, row in group.iterrows():
                df = gpd.read_file(row["file_path"], driver="ESRI Shapefile")
                if row["type"] != 3:
                    df["type"] = row["type"]
                    df["region_id"] = row["region_id"]
                    self.training.append(df)
                else:
                    df["region_id"] = row["region_id"]
                    self.regions.append(df)
        return self

    def combine_training(self) -> ManifestProcessor:
        """Combine the training data into a single GeoDataFrame."""
        self.training = gpd.GeoDataFrame(pd.concat(self.training))
        return self

    def combine_regions(self) -> ManifestProcessor:
        """Combine the regions data into a single GeoDataFrame."""
        self.regions = gpd.GeoDataFrame(pd.concat(self.regions))
        return self

    def reproject_training(self) -> ManifestProcessor:
        """Reproject the GeoDataFrames to EPSG:4326."""
        self.training = self.training.to_crs("EPSG:4326")
        return self

    def reproject_regions(self) -> ManifestProcessor:
        """Reproject the GeoDataFrames to EPSG:4326."""
        self.regions = self.regions.to_crs("EPSG:4326")
        return self

    def re_map(self) -> ManifestProcessor:
        """Re-map the labels to integers. sets the map"""
        labels = self.training[self.label_col].unique().tolist()
        self.map = dict(zip(labels, range(1, len(labels) + 1)))
        self.training = self.training.replace({self.label_col: self.map})
        return self

    def process(self) -> ManifestProcessor:
        """Process the manifest."""
        (
            self.read_manifest()
            .combine_training()
            .combine_regions()
            .reproject_training()
            .reproject_regions()
            .re_map()
        )

        return

    def save_training(self, where: str, fname: str, **kwargs) -> ManifestProcessor:
        """Save the processed data to a csv file."""
        self.training.to_file(os.path.join(where, fname), **kwargs)
        return self

    def save_regions(self, where: str, fname: str, **kwargs) -> ManifestProcessor:
        self.regions.to_file(os.path.join(where, fname), **kwargs)
        return self

    def save_map(self, where: str, **kwargs) -> ManifestProcessor:
        """Save the map to a csv file."""
        pd.DataFrame.from_dict(self.map, orient="index").to_csv(
            os.path.join(where, "map.csv")
        )
        return self


####################################################################################################
# Server Side Functions


def sample_regions(image: ee.Image, **kwargs) -> ee.FeatureCollection:
    """
    Sample regions from an image using the specified parameters.

    Args:
        image (ee.Image): The image to sample regions from.
        **kwargs: Additional keyword arguments to be passed to the `sampleRegions` method.

    Returns:
        ee.FeatureCollection: A feature collection containing the sampled regions.
    """
    return image.sampleRegions(**kwargs)


####################################################################################################
