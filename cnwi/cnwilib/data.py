from __future__ import annotations
import os
from typing import Iterable, Tuple

import geopandas as gpd
import pandas as pd


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
    def __init__(self, labels: list[str]) -> None:
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
class DataProcessor:
    """
    A class for processing training and validation data.

    Attributes:
        training (gpd.GeoDataFrame): The training data.
        validation (gpd.GeoDataFrame): The validation data.
        lookup_table (pd.DataFrame): The lookup table for class names and values.
        processed_data (pd.DataFrame): The processed data.

    Methods:
        process(): Process the training and validation data.

    """

    def __init__(
        self, training: gpd.GeoDataFrame, validation: gpd.GeoDataFrame
    ) -> None:
        """
        Initialize the DataProcessor class.

        Args:
            training (gpd.GeoDataFrame): The training data.
            validation (gpd.GeoDataFrame): The validation data.
        """
        self.training = training
        self.validation = validation
        self.lookup_table = None
        self.processed_data = None

    def process(self) -> DataProcessor:
        """
        Process the training and validation data.

        Returns:
            DataProcessor: The processed data.
        """
        self.training["type"] = 1
        self.validation["type"] = 2

        # combine the training and validation data
        combined = pd.concat([self.training, self.validation])
        combined.to_crs("EPSG:4326", inplace=True)

        # create a lookup table
        labels = combined["class_name"].unique().tolist()
        values = list(range(1, len(labels) + 1))

        combined["class_name"] = combined["class_name"].map(dict(zip(labels, values)))
        self.lookup_table = pd.DataFrame({"class_name": labels, "value": values})
        self.processed_data = combined
        return self


####################################################################################################


def get_shapefile_paths(data_dir: str) -> list[str]:
    """Returns a list of paths to all shapefiles in the data directory."""
    shapefile_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".shp"):
                shapefile_paths.append(os.path.join(root, file))
    return shapefile_paths


def create_raw_data_manifest(file_paths: list[str]) -> pd.DataFrame:
    """Returns a dataframe with the file path, region id, and type of data."""
    df = pd.DataFrame(file_paths, columns=["file_path"])
    # lookup -> map int value to represent type 1, 2, 3 (training, validation, region)
    # region_id
    df["region_id"] = df["file_path"].str.extract(r"(\b\d{1,3}\b)")
    # type assign a int value to each type
    df["type"] = df["file_path"].str.extract(r"/(\w+)(?:Points)?\.shp")
    # training = 0, validation = 1, region = 2
    df["type"] = df["type"].map(
        {"trainingPoints": 1, "validationPoints": 2, "region": 3}
    )
    return df


def process_data_manifest(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Returns a GeoDataFrame with the class name, geometry, type, and region id."""
    processed_gdfs = []

    # ony need to process the training and validation data
    for _, row in df.iterrows():
        if row["type"] == 1 or row["type"] == 2:
            processed_gdfs.append(process_shapefile(row, driver="ESRI Shapefile"))
    return gpd.GeoDataFrame(pd.concat(processed_gdfs))


def process_shapefile(row: pd.Series, **kwargs) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(row["file_path"], kwargs=kwargs)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    gdf["type"] = row["type"]
    gdf["x"] = gdf.geometry.x
    gdf["y"] = gdf.geometry.y
    gdf["region_id"] = row["region_id"]
    return gdf


def create_lookup_table(df: gpd.GeoDataFrame, col: str = None) -> pd.DataFrame:
    col = col or "class_name"
    unique_labels = df[col].unique().tolist()
    return pd.DataFrame(
        {"class_name": unique_labels, "value": list(range(1, len(unique_labels) + 1))}
    )


def create_processed_data_manifest(file_paths: list[str]) -> pd.DataFrame:
    # create a manifest of the processed data and regions
    pass
