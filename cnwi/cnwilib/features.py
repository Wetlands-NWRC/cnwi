import ee
import geopandas as gpd
import pandas as pd


####################################################################################################
# Client functions for preparing data for the CNWI classifiers
####################################################################################################


def insert_values_into_features(
    features: gpd.GeoDataFrame, lookup: pd.DataFrame, column: str = None
) -> gpd.GeoDataFrame:
    column = column or "class_name"
    return features.merge(lookup, on=column, how="inner")


def create_data_lookup(labels: pd.Series) -> pd.DataFrame:
    if not isinstance(labels, pd.Series):
        raise TypeError("labels must be a pandas Series")
    unique_labels = labels.unique().tolist()
    return pd.DataFrame(
        {"class_name": unique_labels, "value": list(range(1, len(unique_labels) + 1))}
    )


def insert_is_training(
    training_features: gpd.GeoDataFrame, testing_features: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    training_features["is_training"] = 1
    testing_features["is_training"] = 0
    return pd.concat([training_features, testing_features]), pd.DataFrame(
        {"is_training": [1, 0], "description": ["training", "testing"]}
    )


####################################################################################################
# Serve side Functions for preparing data for the CNWI classifiers
####################################################################################################


def sample_regions(
    image: ee.Image, features: ee.FeatureCollection, **kwargs
) -> ee.FeatureCollection:
    """Sample the image at the location of each feature in the feature collection.

    Args:
        image (ee.Image): The image to sample
        features (ee.FeatureCollection): The features to sample the image at

    Returns:
        ee.FeatureCollection: The features with the image values added
    """
    return image.sampleRegions(features, **kwargs)
