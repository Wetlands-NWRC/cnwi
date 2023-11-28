import os
from pathlib import Path

from cnwi.cnwilib.data import *
from cnwi.cnwilib.data import gpd


class FeatureBuilder:
    def __init__(self, data_dir: str, out_dir: str = None) -> None:
        self.data_dir = (
            Path(data_dir).absolute().resolve()
        )  # TODO add proper getter and setters for path validation
        self.out_dir = self.data_dir.parent or Path(out_dir)

    def build_features_all(self) -> gpd.GeoDataFrame:
        """output dirs for manifest and lookup table get are created one level up from the data_dir"""
        # get the shapefile paths
        shapefile_paths = get_shapefile_paths(self.data_dir.absolute().resolve())
        # create the data manifest
        # export the manifest to the root of the project dir for reference
        manifest = create_raw_data_manifest(shapefile_paths)
        manifest_dir = self.out_dir / "manifests"
        if not manifest_dir.exists():
            os.mkdir(manifest_dir)

        manifest.to_csv(os.path.join(manifest_dir, "data_manifest.csv"), index=False)

        # process the data manifest
        all_gdf = process_data_manifest(manifest)

        # cast crs
        all_gdf.to_crs(epsg=4326, inplace=True)

        # create the lookup table
        lookup_table = create_lookup_table(all_gdf)
        lookup_table_dir = self.out_dir / "reference"
        if not lookup_table_dir.exists():
            os.mkdir(lookup_table_dir)
        lookup_table.to_csv(lookup_table_dir / "lookup_table.csv", index=False)

        # save the all_gdf to file
        all_gdf_dir = self.out_dir / "data" / "processed"
        if not all_gdf_dir.exists():
            os.makedirs(all_gdf_dir)
        all_gdf.to_file(all_gdf_dir / "all_data.shp")

        return all_gdf


class OpsFeatureBuilder(FeatureBuilder):
    def build_features(self, data_dir: str) -> gpd.GeoDataFrame:
        return super().build_features(data_dir)
