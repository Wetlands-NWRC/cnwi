import ee
import geopandas as gpd
import pandas as pd


####################################################################################################
# Client functions for preparing data for the CNWI classifiers
####################################################################################################


def insert_values_into_features(
    features: gpd.GeoDataFrame, values: pd.Series
) -> gpd.GeoDataFrame:
    pass


def create_data_lookup(labels: list[str] | pd.Series) -> pd.DataFrame:
    pass


def add_region_to_features():
    pass


def insert_is_training(
    training_features: gpd.GeoDataFrame, testing_features: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    pass


def load_from_data_manifest(manifest: pd.DataFrame) -> gpd.GeoDataFrame:
    pass


def make_data_manifest(file_paths: list[str]) -> pd.DataFrame:
    pass


####################################################################################################
# Serve side Functions for preparing data for the CNWI classifiers
####################################################################################################


def sample_regions(
    image: ee.Image, features: ee.FeatureCollection, **kwargs
) -> ee.FeatureCollection:
    pass
