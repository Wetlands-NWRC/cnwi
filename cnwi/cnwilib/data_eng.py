from __future__ import annotations

import os

from typing import Any, Tuple
from zipfile import ZipFile

import ee
import geopandas as gpd
import pandas as pd


####################################################################################################
def data_manifest(data_dir: str) -> pd.DataFrame:
    """Creates a manifest of the data files in the specified directory.

    Args:
        data_dir (str): The directory path where the data is located.

    Returns:
        pd.DataFrame: A dataframe containing the manifest.
    """
    M = {"trainingPoints": 1, "validationPoints": 2, "region": 3}
    shapefile_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".shp"):
                shapefile_paths.append(os.path.join(root, file))

    manifest = pd.DataFrame(shapefile_paths, columns=["file_path"])
    manifest["ECOREGION_ID"] = (
        manifest["file_path"].str.extract(r"(\b\d{1,3}\b)").astype(int)
    )
    manifest["type"] = manifest["file_path"].str.extract(r"/(\w+)(?:Points)?\.shp")
    manifest["type"] = manifest["type"].replace(M)
    manifest = manifest.sort_values(by=["ECOREGION_ID", "type"]).reset_index(drop=True)
    return manifest


def process_data_manifest(
    manifest: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Process the data manifest.

    Args:
        manifest (pd.DataFrame): The data manifest.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple containing the processed training, regions, class ref data.
    """
    training = []
    regions = []
    for _, group in manifest.groupby("ECOREGION_ID"):
        for _, row in group.iterrows():
            df = gpd.read_file(row["file_path"], driver="ESRI Shapefile")
            if row["type"] != 3:
                df["type"] = row["type"]
                df["ECOREGION_ID"] = row["ECOREGION_ID"]
                training.append(df)
            else:
                df["ECOREGION_ID"] = row["ECOREGION_ID"]
                regions.append(df)

    training = gpd.GeoDataFrame(pd.concat(training))
    regions = gpd.GeoDataFrame(pd.concat(regions))

    training = training.to_crs("EPSG:4326")
    regions = regions.to_crs("EPSG:4326")

    labels = training["class_name"].unique().tolist()
    map = dict(zip(labels, range(1, len(labels) + 1)))
    lookup = pd.DataFrame.from_dict(map, orient="index")
    training = training.replace({"class_name": map})

    return training, regions, lookup


# Client Side Functions and Classes
####################################################################################################


def split_and_zip(
    gdf: gpd.GeoDataFrame, groupby_col: str, where, file_prefix: str = None
) -> None:
    """
    Compresses and archives GeoDataFrame groups based on a specified column.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame containing the data to be grouped and compressed.
        groupby_col (str): The column name to group the GeoDataFrame by.
        where: The directory path where the compressed files will be saved.
        file_prefix (str, optional): The prefix to be used for the compressed file names. Defaults to None.

    Returns:
        None
    """

    scratch = where / "scratch"
    scratch.mkdir(exist_ok=True)

    for _, group in gdf.groupby(groupby_col):
        # save each group
        file_prefix = file_prefix or "features"
        group.to_file(scratch / f"{file_prefix}_{_}.shp", driver="ESRI Shapefile")
        archive_name = f"{file_prefix}_{_}"
        # compress each dataset
        with ZipFile(scratch / f"{archive_name}.zip", "w") as zip:
            zip.write(scratch / f"{archive_name}.shp")
            zip.write(scratch / f"{archive_name}.dbf")
            zip.write(scratch / f"{archive_name}.prj")
            zip.write(scratch / f"{archive_name}.shx")
            zip.write(scratch / f"{archive_name}.cpg")

        # move the zip file to the processed directory
        (where / "zipped").mkdir(exist_ok=True)
        (scratch / f"{archive_name}.zip").rename(
            where / "zipped" / f"{archive_name}.zip"
        )

        # clean up the scratch directory
        (scratch / f"{archive_name}.shp").unlink()
        (scratch / f"{archive_name}.dbf").unlink()
        (scratch / f"{archive_name}.prj").unlink()
        (scratch / f"{archive_name}.shx").unlink()
        (scratch / f"{archive_name}.cpg").unlink()
        # output processed/shapefile AND processed/zipped

    # remove the scratch directory
    scratch.rmdir()


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
