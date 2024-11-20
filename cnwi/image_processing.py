import ee

from sensors import DataCube
from rmath import compute_ndvi_from_expression, compute_savi_from_expression


def process_datacube(aoi: ee.Geometry, data_cube: DataCube) -> ee.Image:
    
    if not isinstance(data_cube, DataCube):
        raise ValueError("data_cube must be an instance of DataCube")

    # -- base dataset
    dc = data_cube.filterBounds(aoi)

    # -- reduce to image
    dc_image = dc.mosaic()

    # -- select spring spectral bands
    dc_image_spring = (
        dc_image
        .select("a_spri_b0[2-9].*|a_spri_b[1-2].*")
        .rename(["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"])
    )

    # -- add ndvi, tc, savi
    dc_image_spring = (
        dc_image_spring
        .addBands(compute_ndvi_from_expression(dc_image_spring, "B8", "B4"))
        .addBands(compute_savi_from_expression("B8", "B4")(dc_image_spring))
    )

    # -- Summer
    dc_image_summer = (
        dc_image
        .select("b_summ_b0[2-9].*|b_summ_b[1-2].*")
        .rename(["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"])
    )

    # -- add ndvi, tc, savi
    dc_image_summer = (
        dc_image_summer
        .addBands(compute_ndvi_from_expression(dc_image_summer, "B8", "B4"))
        .addBands(compute_savi_from_expression("B8", "B4")(dc_image_summer))
    )

    # -- Fall
    dc_image_fall = (
        dc_image
        .select("c_fall_b0[2-9].*|c_fall_b[1-2].*")
        .rename(["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"])
    )

    # -- add ndvi, tc, savi
    dc_image_fall = (
        dc_image_fall
        .addBands(compute_ndvi_from_expression(dc_image_fall, "B8", "B4"))
        .addBands(compute_savi_from_expression("B8", "B4")(dc_image_fall))
    )

    # -- stack
    return ee.Image.cat(dc_image_spring, dc_image_summer, dc_image_fall)