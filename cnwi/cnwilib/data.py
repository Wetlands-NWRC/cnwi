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

    def __init__(self, data_dir: str) -> None:
        """
        Initialize the Data class.

        Args:
            data_dir (str): The directory path where the data is located.
        """
        self.manifest = data_dir

    def __iter__(self) -> Iterable[Tuple[str, pd.DataFrame]]:
        """Iterates over the manifest, yielding region IDs and corresponding dataframes."""
        for idx, df in self.manifest.groupby("region_id"):
            yield idx, df

    @property
    def manifest(self) -> pd.DataFrame:
        """Getter for the manifest dataframe."""
        return self._manifest

    @manifest.setter
    def manifest(self, data_dir: str) -> None:
        """Setter for the manifest dataframe, creates and processes the dataframe."""
        # TODO need to add a check to see if the data_dir is a directory
        # TODO need to add a check to see if the data_dir is empty
        # TODO need to ensure that all data are valid files
        df = self._create_base_manifest(data_dir)
        self._manifest = self._process_manifest(df)

    @property
    def training(self) -> pd.DataFrame:
        """Getter for the training data."""
        return self.manifest[self.manifest["type"] == 1]

    @property
    def validation(self) -> pd.DataFrame:
        """Getter for the validation data."""
        return self.manifest[self.manifest["type"] == 2]

    @property
    def regions(self) -> pd.DataFrame:
        """Getter for the regions data."""
        return self.manifest[self.manifest["type"] == 3]

    @property
    def file_paths(self) -> pd.DataFrame:
        """Getter for the file paths."""
        return self.manifest[["file_path"]]

    @staticmethod
    def _create_base_manifest(data_dir: str) -> pd.DataFrame:
        """Creates the base state of the manifest."""
        shapefile_paths = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".shp"):
                    shapefile_paths.append(os.path.join(root, file))

        return pd.DataFrame(shapefile_paths, columns=["file_path"])

    @staticmethod
    def _process_manifest(df: pd.DataFrame) -> gpd.GeoDataFrame:
        """Processes the manifest dataframe, extracting region IDs and assigning types."""
        df["region_id"] = df["file_path"].str.extract(r"(\b\d{1,3}\b)")
        # type assign a int value to each type
        df["type"] = df["file_path"].str.extract(r"/(\w+)(?:Points)?\.shp")
        # training = 1, validation = 2, region = 3
        df["type"] = df["type"].map(
            {"trainingPoints": 1, "validationPoints": 2, "region": 3}
        )
        return df

    def save(self, where: str) -> Manifest:
        """Save the manifest to a csv file.

        Args:
            where (str): The path to save the csv file.

        Returns:
            Manifest: The Manifest instance.
        """
        # TODO add a check to see if the file already exists
        # TODO if the root directory is not a directory, create it
        self.manifest.to_csv(where, index=False)
        return self


class LookupTable:
    def __init__(self, labels: list[str] = None) -> None:
        self.labels = labels

    @property
    def values(self) -> list[int]:
        return list(range(1, len(self.labels) + 1))

    @property
    def mapper(self) -> dict[str, dict[str, int]]:
        return dict(zip(self.labels, self.values))

    @property
    def table(self) -> pd.DataFrame:
        return pd.DataFrame({"class_name": self.labels, "value": self.values})

    def save(self, where: str) -> LookupTable:
        self.table.to_csv(where, index=False)
        return self


####################################################################################################
def process_shapefile(row: pd.Series, **kwargs) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(row["file_path"], kwargs=kwargs)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    gdf["type"] = row["type"]
    gdf["region_id"] = row["region_id"]
    return gdf


def process_data_manifest(
    manifest: Manifest, label_col: str
) -> Tuple[gpd.GeoDataFrame, LookupTable]:
    """Returns a GeoDataFrame with the class name, geometry, type, and region id."""
    processed_gdfs = []

    # ony need to process the training and validation data
    for _, group in manifest:
        for _, row in group[group["type"] != 3].iterrows():
            gdf = process_shapefile(row, driver="ESRI Shapefile")
            processed_gdfs.append(gdf)
    combined = gpd.GeoDataFrame(pd.concat(processed_gdfs))
    lookup_table = LookupTable(combined[label_col].unique().tolist())
    combined[label_col] = combined[label_col].map(lookup_table.mapper)
    return combined, lookup_table


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
