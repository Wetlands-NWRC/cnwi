import click

from pathlib import Path


@click.group()
def cli():
    pass


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), required=True)
def ingest(input, output):
    from cnwi.cnwilib.ingest import ingest_data

    p = Path(output)
    if not p.exists():
        p.mkdir(parents=True)
    ingest_data(input, output)


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), required=True)
def build_features(input, output):
    """Builds features from a GeoJSON file"""
    from cnwi.cnwilib import data_eng as de

    manifest = de.data_manifest(input)
    training, regions, lookup = de.process_data_manifest(manifest)

    output_dir = Path(output)
    if not output_dir.exists():
        output_dir.mkdir()

    training.to_file(output_dir / "training.geojson", driver="GeoJSON")
    regions.to_file(output_dir / "regions.geojson", driver="GeoJSON")
    lookup.to_csv(output_dir / "lookup.csv")

    de.split_and_zip(training, "ECOREGION_ID", output_dir)
    de.split_and_zip(regions, "ECOREGION_ID", output_dir, "regions")
