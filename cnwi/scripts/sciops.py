import sys
import os
import ee
import geopandas as gpd

from cnwi.cnwilib import data_eng
from cnwi.cnwilib import features
from cnwi.cnwilib.image import ImageDirector, ImageBuilder, ImageStack


def main():
    if len(sys.argv) < 3:
        print("Usage: python sciops.py payload data_dir")
        sys.exit(1)

    payload = sys.argv[1]
    print(f"Payload: {payload}")
    data_dir = sys.argv[2]
    print(f"Data directory: {data_dir}")

    shapefile_paths = data_eng.get_shapefile_paths(data_dir)
    manifest = data_eng.create_raw_data_manifest(shapefile_paths)

    for _, group in manifest.groupby("region_id"):
        if not ee.data._credentials:
            ee.Initialize()
        print("Processing region:")
        print(_)
        # this process the training and validation data
        gdf = data_eng.process_data_manifest(group)
        gdf.to_crs(epsg=4326, inplace=True)
        print("Training and validation data:")
        print(gdf.head())
        region = gpd.read_file(group[group["type"] == 3]["file_path"].values[0])
        region.to_crs(epsg=4326, inplace=True)
        print("Region:")
        print(region.head())
        print("#" * 80)
        ee_region = ee.FeatureCollection(region.__geo_interface__).geometry()
        ee_data = ee.FeatureCollection(gdf.__geo_interface__)
        print(ee_data.first().getInfo())
        # data.process_data_manifest(group)

        # TODO create a function that will exicute the build process for sciops image inputs
        # image inputs
        stack = ImageStack()

        # data cube
        data_cube_image = (
            ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(ee_region).mosaic()
        )
        data_cube_bldr = ImageBuilder().image = data_cube_image
        data_cube_director = ImageDirector(data_cube_bldr)
        data_cube_director.build_data_cube(ee_region)

        # build the image inputs

        # reset the processing environment
        # ee.Reset()


if __name__ == "__main__":
    ee.Initialize()
    main()
