from __future__ import annotations
from math import pi
from typing import Callable, Any

# Remote Sensing Data Processing
# cnwi/rsdproc.py


# helper functions for computation of SAVI, NDVI, and Tasseled Cap, Ratio
import ee
from ee.featurecollection import FeatureCollection
from ee.geometry import Geometry
from ee.imagecollection import ImageCollection


# SAR Processing and Datasets


###############################################################################################


def s1_dataset(constructor: Any, aoi) -> tuple[ee.Image, ee.Image]:
    dataset = (
        ee.ImageCollection(constructor)
        .filterBounds(aoi)
        .select("V.*")
        .map(lambda x: x.convolve(ee.Kernel.square(1)))
        .map(
            lambda x: x.addBands(x.select("VV").divide(x.select("VH")).rename("VV_VH"))
        )
    )
    es = dataset.filterDate("2017-01-01", "2017-12-31").mosaic()
    ls = dataset.filterDate("2018-01-01", "2018-12-31").mosaic()
    return es, ls


def alos_dataset(aoi) -> ee.Image:
    start, end = "2018", "2021"
    dataset = (
        ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR")
        .filterBounds(aoi)
        .filterDate(start, end)
        .map(lambda x: x.convolve(ee.Kernel.square(1)))
        .map(
            lambda x: x.addBands(x.select("HH").divide(x.select("HV")).rename("HH_HV"))
        )
        .median()
    )
    return dataset


###############################################################################################


def compute_ndvi(nir: str, red: str) -> Callable[[ee.Image], ee.Image]:
    """
    Computes the NDVI from the NIR and red bands.

    Args:
        nir (str): The name of the NIR band.
        red (str): The name of the red band.

    Returns:
        Callable[[ee.Image], ee.Image]: A function that computes the NDVI.
    """
    return lambda image: image.addBands(
        image.normalizedDifference([nir, red]).rename("NDVI")
    )


def compute_savi(nir: str, red: str, l: float = 0.5) -> Callable[[ee.Image], ee.Image]:
    """
    Computes the SAVI from the NIR and red bands.

    Args:
        nir (str): The name of the NIR band.
        red (str): The name of the red band.
        l (float, optional): The SAVI coefficient. Defaults to 0.5.

    Returns:
        Callable[[ee.Image], ee.Image]: A function that computes the SAVI.
    """
    return lambda image: image.addBands(
        image.expression(
            "(1 + L) * (NIR - RED) / (NIR + RED + L)",
            {"NIR": image.select(nir), "RED": image.select(red), "L": l},
        ).rename("SAVI")
    )


def compute_tasseled_cap(
    blue: str, green: str, red: str, nir: str, swir1: str, swir2: str
):
    """
    Adds the Tasseled Cap bands to an image.

    Args:
        blue (str): The name of the blue band.
        green (str): The name of the green band.
        red (str): The name of the red band.
        nir (str): The name of the NIR band.
        swir1 (str): The name of the SWIR1 band.
        swir2 (str): The name of the SWIR2 band.

    Returns:
        ee.Image: The image with the Tasseled Cap bands added.
    """

    def compute(image: ee.Image):
        coefficients = ee.Array(
            [
                [0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872],
                [-0.2941, -0.243, -0.5424, 0.7276, 0.0713, -0.1608],
                [0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559],
                [-0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773],
                [-0.3294, 0.0557, 0.1056, 0.1855, -0.4349, 0.8085],
                [0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252],
            ]
        )

        image_inpt = image.select([blue, green, red, nir, swir1, swir2])
        array_image = image_inpt.toArray()
        array_image_2d = array_image.toArray(1)

        components = (
            ee.Image(coefficients)
            .matrixMultiply(array_image_2d)
            .arrayProject([0])
            .arrayFlatten(
                [["brightness", "greenness", "wetness", "fourth", "fifth", "sixth"]]
            )
        )
        components = components.select(["brightness", "greenness", "wetness"])
        return image.addBands(components)

    return compute


def data_cube_dataset(dataset_id, aoi) -> ee.Image:

    spring_bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
    summer_bands = [f"{band}_1" for band in spring_bands]
    fall_bands = [f"{band}_2" for band in spring_bands]

    bands = spring_bands + summer_bands + fall_bands
    b_pattern = "a_spri_b0[2-9].*|a_spri_b[1-2].*|b_summ_b0[2-9].*|b_summ_b[1-2].*|c_fall_b0[2-9].*|c_fall_b[1-2].*"

    dataset = ee.ImageCollection(dataset_id).filterBounds(aoi).select(b_pattern)

    original_bands = dataset.first().bandNames()
    dataset = (
        dataset.select(original_bands, bands)
        .map(compute_ndvi("B8", "B4"))
        .map(compute_ndvi("B8_1", "B4_1"))
        .map(compute_ndvi("B8_2", "B4_2"))
        .map(compute_savi("B8", "B4"))
        .map(compute_savi("B8_1", "B4_1"))
        .map(compute_savi("B8_2", "B4_2"))
        .map(compute_tasseled_cap("B2", "B3", "B4", "B8", "B11", "B12"))
        .map(compute_tasseled_cap("B2_1", "B3_1", "B4_1", "B8_1", "B11_1", "B12_1"))
        .map(compute_tasseled_cap("B2_2", "B3_2", "B4_2", "B8_2", "B11_2", "B12_2"))
    )
    return dataset.mosaic()


def compute_s2_time_series(aoi, modes: int = 3) -> ImageCollection:
    mk_freq = lambda x, y: [f"{x}_{y}" for y in range(1, modes + 1)]

    def cloud_mask(image: ee.Image):
        qa = image.select("QA60")

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = (
            qa.bitwiseAnd(cloud_bit_mask)
            .eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        )

        return image.updateMask(mask)

    def add_time(image: ee.Image):
        date = image.date()
        years = date.difference(ee.Date("1970-01-01"), "year")
        time_radians = ee.Image(years.multiply(2 * pi))
        return image.addBands(time_radians.rename("t").float())

    def add_harmonics(frequencies: list[int], cos_names, sin_names):
        def wrapper(image: ee.Image):
            frequencies = ee.Image.constant(frequencies)
            time = ee.Image(image).select("t")
            cos_img = time.multiply(frequencies).cos().rename(cos_names)
            sin_img = time.multiply(frequencies).sin().rename(sin_names)
            return image.addBands(cos_img).addBands(sin_img)

        return wrapper

    def compute_phase(mode: int, cos_name: str, sin_name: str):
        def wrapper(image: ee.Image):
            phase = ee.Image(
                image.select(cos_name)
                .atan2(image.select(sin_name))
                .rename(f"phase_{mode}")
            )
            return image.addBands(phase)

        return wrapper

    def compute_amplitude(mode: int, cos_name: str, sin_name: str):
        def wrapper(image: ee.Image):
            amplitude = ee.Image(
                image.select(cos_name)
                .hypot(image.select(sin_name))
                .rename(f"amplitude_{mode}")
            )
            return image.addBands(amplitude)

        return wrapper

    ## TS Processing starts here

    cos_name = mk_freq("cos", modes)
    sin_name = mk_freq("sin", modes)

    dependent = "NDVI"
    independent = ["t", "constant"] + cos_name + sin_name

    dataset = (
        ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        .filterBounds(aoi)
        .filterDate("2017-01-01", "2022-12-31")
        .map(cloud_mask)
        .map(compute_ndvi("B8", "B4"))
        .select("NDVI")
        .map(lambda x: x.addBands(ee.Image(1)))
        .map(add_time)
        .map(add_harmonics(list(range(1, modes + 1)), cos_name, sin_name))
    )

    harmonic_trend = dataset.select(independent + [dependent]).reduce(
        ee.Reducer.linearRegression(len(independent), 1)
    )

    harmonic_coeff = harmonic_trend.select("coefficients").arrayFlatten(
        [independent, ["coef"]]
    )

    dataset = dataset.map(lambda x: x.addBands(harmonic_coeff))

    for mode in range(1, modes + 1):
        dataset = dataset.map(compute_phase(mode, f"cos_{mode}", f"sin_{mode}"))
        dataset = dataset.map(compute_amplitude(mode, f"cos_{mode}", f"sin_{mode}"))

    return dataset.median().select(f"{dependent}|.*coef|amp.*|phase.*").unitScale(-1, 1)
