import click
import geopandas as gpd
import pandas as pd

from pathlib import Path


@click.group()
def cli():
    pass


@cli.command()
@click.argument("training")
@click.argument("validation")
def build_features(training, validation, region):
    """Builds features from a GeoJSON file"""
    click.echo(training)
    gdf_train = gpd.read_file(training, driver="ESRI Shapefile")
    gdf_train["split"] = "train"

    click.echo(validation)
    gdf_test = gpd.read_file(validation, driver="ESRI Shapefile")
    gdf_test["split"] = "test"

    gdf = pd.merge([gdf_train, gdf_test])
    gdf = gdf.to_crs("EPSG:4326")

    click.echo(region)


@cli.command()
@click.argument("file")
def prep_for_ee(file):
    pass


if __name__ == "__main__":
    cli()
