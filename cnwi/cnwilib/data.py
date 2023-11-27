import os

import geopandas as gpd
import pandas as pd


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
    gdf["type"] = row["type"]
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
