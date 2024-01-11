from __future__ import annotations

# Remote Sensing Data Processing
# cnwi/rsdproc.py


# helper functions for computation of SAVI, NDVI, and Tasseled Cap, Ratio
import ee
from ee.featurecollection import FeatureCollection
from ee.geometry import Geometry
from ee.imagecollection import ImageCollection


# Calculators
def add_ndvi(nir: str, red: str):
    """
    Adds the NDVI band to an image.

    Args:
        nir (str): The name of the NIR band.
        red (str): The name of the red band.

    Returns:
        ee.Image: The image with the NDVI band added.
    """
    return lambda image: image.addBands(
        image.normalizedDifference([nir, red]).rename("NDVI")
    )


def add_savi(nir: str, red: str, l: float = 0.5):
    """
    Adds the SAVI band to an image.

    Args:
        nir (str): The name of the NIR band.
        red (str): The name of the red band.
        l (float, optional): The SAVI coefficient. Defaults to 0.5.

    Returns:
        ee.Image: The image with the SAVI band added.
    """
    return lambda image: image.addBands(
        image.expression(
            "(1 + L) * (NIR - RED) / (NIR + RED + L)",
            {"NIR": image.select(nir), "RED": image.select(red), "L": l},
        ).rename("SAVI")
    )


def add_tasseled_cap(blue: str, green: str, red: str, nir: str, swir1: str, swir2: str):
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


def ratio(b1, b2, name):
    """
    Adds the ratio band to an image.

    Args:
        b1 (str): The name of the first band.
        b2 (str): The name of the second band.
        name (str): The name of the ratio band.

    Returns:
        ee.Image: The image with the ratio band added.
    """
    return lambda image: image.addBands(
        image.expression(
            "((NIR - RED) / (NIR + RED + 0.5)) * (1.5)",
            {"NIR": image.select(b1), "RED": image.select(b2)},
        ).rename(name)
    )


###############################################################################################
# Filters for Sentinel 1
def boxcar(image: ee.Image) -> ee.Image:
    """
    Applies a boxcar filter to the input image.

    Args:
        image (ee.Image): The input image to be filtered.

    Returns:
        ee.Image: The filtered image.
    """
    return image.convolve(ee.Kernel.square(1))


###############################################################################################


class RSDProc:
    """Remote Sensing Data Processing"""

    def __init__(
        self,
        collection: ee.ImageCollection,
        region: ee.Geometry | ee.FeatureCollection,
        start_date: str = None,
        end_date: str = None,
    ) -> None:
        self.collection = collection
        self.region = region
        self.start_date = start_date
        self.end_date = end_date

    def __add__(self, other: RSDProc) -> RSDProc:
        self.collection = self.collection.merge(other.collection)
        return self

    def filter_geometry(self) -> RSDProc:
        self.collection = self.collection.filterBounds(self.region)
        return self

    def filter_date(self) -> RSDProc:
        if self.start_date or self.end_date:
            return self
        self.collection = self.collection.filterDate(self.start_date, self.end_date)
        return self

    def select_bands(self, pattern: str) -> RSDProc:
        self.collection = self.collection.select(pattern)
        return self

    def rename_bands(self, selectors: list[str], names: list[str]) -> RSDProc:
        self.collection = self.collection.select(selectors, names)
        return self

    def add_func(self, func: callable) -> RSDProc:
        self.collection = self.collection.map(func)
        return self

    def process(self) -> RSDProc:
        return self


class DataCubeProc(RSDProc):
    """Data Cube Processing"""

    BAND_NAMES = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]

    def __init__(self, collection: ee.ImageCollection, region) -> None:
        super().__init__(collection, region, None, None)

    def select_spectral_bands(self) -> DataCubeProc:
        p = "a_spri_b0[2-9].*|a_spri_b[1-2].*|b_summ_b0[2-9].*|b_summ_b[1-2].*|c_fall_b0[2-9].*|c_fall_b[1-2].*"
        self.select_bands(p)
        return self

    def rename_spectral_bands(self) -> DataCubeProc:
        bands = self._mk_band_names(self.BAND_NAMES)
        self.rename_bands(self.collection.first().bandNames(), bands)
        return self

    def add_spring_ndvi(self) -> DataCubeProc:
        self.add_func(add_ndvi("B8", "B4"))
        return self

    def add_spring_savi(self) -> DataCubeProc:
        self.add_func(add_savi("B8", "B4"))
        return self

    def add_spring_tasseled_cap(self) -> DataCubeProc:
        self.add_func(add_tasseled_cap("B2", "B3", "B4", "B8", "B11", "B12"))
        return self

    def add_summer_ndvi(self) -> DataCubeProc:
        self.add_func(add_ndvi("B8_1", "B4_1"))
        return self

    def add_summer_savi(self) -> DataCubeProc:
        self.add_func(add_savi("B8_1", "B4_1"))
        return self

    def add_summer_tasseled_cap(self) -> DataCubeProc:
        self.add_func(
            add_tasseled_cap("B2_1", "B3_1", "B4_1", "B8_1", "B11_1", "B12_1")
        )
        return self

    def add_fall_ndvi(self) -> DataCubeProc:
        self.add_func(add_ndvi("B8_2", "B4_2"))
        return self

    def add_fall_savi(self) -> DataCubeProc:
        self.add_func(add_savi("B8_2", "B4_2"))
        return self

    def add_fall_tasseled_cap(self) -> DataCubeProc:
        self.add_func(
            add_tasseled_cap("B2_2", "B3_2", "B4_2", "B8_2", "B11_2", "B12_2")
        )
        return self

    def process(self) -> DataCubeProc:
        (
            self.filter_geometry()
            .select_spectral_bands()
            .rename_spectral_bands()
            .add_spring_ndvi()
            .add_spring_savi()
            .add_spring_tasseled_cap()
            .add_summer_ndvi()
            .add_summer_savi()
            .add_summer_tasseled_cap()
            .add_fall_ndvi()
            .add_fall_savi()
            .add_fall_tasseled_cap()
        )
        return self

    @staticmethod
    def _mk_band_names(bands: list[str]) -> list[str]:
        summer = [f"{band}_1" for band in bands]
        fall = [f"{band}_2" for band in bands]
        return bands + summer + fall


class S1Proc(RSDProc):
    """Sentinel 1 Processing"""

    def __init__(
        self,
        collection: ee.ImageCollection,
        region: ee.Geometry | ee.FeatureCollection,
        start_date: str = None,
        end_date: str = None,
    ) -> None:
        super().__init__(collection, region, start_date, end_date)

    def denoise(self) -> S1Proc:
        self.add_func(boxcar)
        return self

    def add_ratio(self):
        self.add_func(ratio("VV", "VH", "VV_VH"))
        return self

    def process(self) -> S1Proc:
        (self.filter_geometry().filter_date().select_bands("V.*").denoise().add_ratio())
        return self


class ALOSProc(RSDProc):
    """ALOS Processing"""

    def __init__(
        self,
        region: ee.Geometry | ee.FeatureCollection,
        start_date: str,
        end_date: str,
    ) -> None:
        super().__init__(
            ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH"),
            region,
            start_date,
            end_date,
        )

    def denoise(self) -> ALOSProc:
        self.add_func(boxcar)
        return self

    def add_ratio(self) -> ALOSProc:
        self.add_func(ratio("HH", "HV", "HH_HV"))
        return self

    def process(self) -> ALOSProc:
        (self.filter_geometry().filter_date().select_bands("H.*").denoise().add_ratio())
        return self


class S2Proc(RSDProc):
    def __init__(
        self,
        region: Geometry | FeatureCollection,
        start_date: str,
        end_date: str,
    ) -> None:
        super().__init__(
            ee.ImageCollection("COPERNICUS/S2_HARMONIZED"), region, start_date, end_date
        )

    def filter_cloud_cover(self, max_cloud_cover: float = 20) -> S2Proc:
        self.collection = self.collection.filter(
            ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover)
        )
        return self

    def add_cloud_mask(self) -> S2Proc:
        def _mask(image: ee.Image):
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

        self.add_func(_mask)
        return self

    def add_ndvi(self) -> S2Proc:
        self.add_func(add_ndvi("B8", "B4"))
        return self

    def add_savi(self) -> S2Proc:
        self.add_func(add_savi("B8", "B4"))
        return self

    def add_tasseled_cap(self) -> S2Proc:
        self.add_func(add_tasseled_cap("B2", "B3", "B4", "B8", "B11", "B12"))
        return self

    def process(self) -> S2Proc:
        (
            self.filter_geometry()
            .filter_date()
            .filter_cloud_cover()
            .add_cloud_mask()
            .add_ndvi()
            .add_savi()
            .add_tasseled_cap()
        )
        return self
