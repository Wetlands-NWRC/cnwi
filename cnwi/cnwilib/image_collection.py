from __future__ import annotations
import ee
from typing import Any

from math import pi

from ee.imagecollection import ImageCollection

from cnwi.cnwilib.image import NDVI, SAVI, TasseledCap, Ratio


class TimeSeries:
    def __init__(
        self, collection: ee.ImageCollection, dependent: str, modes: int = 3
    ) -> None:
        self.collection = collection
        self.dependent = dependent
        self.independent = []
        self.modes = modes

    def __add_independent(self, independent: str | list[str]) -> None:
        if isinstance(independent, str) and independent not in self.independent:
            self.independent.append(independent)
        elif isinstance(independent, list) and all(
            isinstance(i, str) for i in independent
        ):
            self.independent.extend(independent)
        else:
            raise TypeError(
                "Independent variable must be a string or a list of strings."
            )

    def _mk_freq_name(self, name: str) -> list[str]:
        return [f"{name}_{i}" for i in range(1, self.modes + 1)]

    def _add_constant(self) -> TimeSeries:
        def _add_const_inner(image):
            return image.addBands(ee.Image(1))

        self.__add_independent("constant")
        self.collection = self.collection.map(_add_const_inner)
        return self

    def _add_time(self) -> TimeSeries:
        def _add_time_inner(image):
            date = image.date()
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi))
            return image.addBands(time_radians.rename("t").float())

        self.__add_independent("t")
        self.collection = self.collection.map(_add_time_inner)
        return self

    def _add_harmonics(self) -> TimeSeries:
        cos = self._mk_freq_name("cos")
        sin = self._mk_freq_name("sin")

        def _add_harmonics_inner(image):
            frequencies = ee.Image.constant(list(range(1, self.modes + 1)))
            time = ee.Image(image).select("t")
            cos_img = time.multiply(frequencies).cos().rename(cos)
            sin_img = time.multiply(frequencies).sin().rename(sin)
            return image.addBands(cos_img).addBands(sin_img)

        self.__add_independent(cos)
        self.__add_independent(sin)
        self.collection = self.collection.map(_add_harmonics_inner)
        return self

    def build(self) -> TimeSeries:
        # TODO add property to set if build has been run
        self._add_constant()
        self._add_time()
        self._add_harmonics()
        return self


####################################################################################################
def process_data_cube(
    collection_id: str, region: ee.Geometry | ee.FeatureCollection
) -> DataCubeProcessor:
    """
    Process a data cube for a given collection ID and region.

    Args:
        collection_id (str): The ID of the image collection.
        region (ee.Geometry | ee.FeatureCollection): The region of interest.

    Returns:
        DataCubeProcessor: The processed data cube.
    """
    collection = ee.ImageCollection(collection_id).filterBounds(region)
    return DataCubeProcessor(collection).process()


class DataCubeProcessor:
    BAND_NAMES = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]

    def __init__(self, collection: ee.ImageCollection) -> None:
        self.collection = collection

    def select_spectral_bands(self) -> DataCubeProcessor:
        self.collection = self.collection.select(
            "a_spri_b0[2-9].*|a_spri_b[1-2].*|b_summ_b0[2-9].*|b_summ_b[1-2].*|c_fall_b0[2-9].*|c_fall_b[1-2].*"
        )
        return self

    def rename_bands(self):
        spring_bands = [f"{b}_1" for b in self.BAND_NAMES]
        summer_bands = [f"{b}_2" for b in self.BAND_NAMES]
        fall_bands = [f"{b}_3" for b in self.BAND_NAMES]

        cur_bands = self.collection.first().bandNames()
        dest_bands = spring_bands + summer_bands + fall_bands
        self.collection = self.collection.select(cur_bands, dest_bands)
        return self

    def add_spring_ndvi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(NDVI("B8_1", "B4_1", "NDVI_1"))
        return self

    def add_spring_savi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(SAVI("B8_1", "B4_1", "SAVI_1"))
        return self

    def add_spring_tasseled_cap(self) -> DataCubeProcessor:
        self.collection = self.collection.map(
            TasseledCap(
                blue="B2_1",
                green="B3_1",
                red="B4_1",
                nir="B8_1",
                swir1="B11_1",
                swir2="B12_1",
            )
        )
        return self

    def add_summer_ndvi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(NDVI("B8_2", "B4_2", "NDVI_2"))
        return self

    def add_summer_savi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(SAVI("B8_2", "B4_2", "SAVI_2"))
        return self

    def add_summer_tasseled_cap(self) -> DataCubeProcessor:
        self.collection = self.collection.map(
            TasseledCap(
                blue="B2_2",
                green="B3_2",
                red="B4_2",
                nir="B8_2",
                swir1="B11_2",
                swir2="B12_2",
            )
        )
        return self

    def add_fall_ndvi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(NDVI("B8_3", "B4_3", "NDVI_3"))
        return self

    def add_fall_savi(self) -> DataCubeProcessor:
        self.collection = self.collection.map(SAVI("B8_3", "B4_3", "SAVI_3"))
        return self

    def add_fall_tasseled_cap(self) -> DataCubeProcessor:
        self.collection = self.collection.map(
            TasseledCap(
                blue="B2_3",
                green="B3_3",
                red="B4_3",
                nir="B8_3",
                swir1="B11_3",
                swir2="B12_3",
            )
        )
        return self

    def transform(self) -> DataCubeProcessor:
        self.collection = self.collection.mosaic()
        return self

    def process(self) -> DataCubeProcessor:
        (
            self.select_spectral_bands()
            .rename_bands()
            .add_spring_ndvi()
            .add_spring_savi()
            .add_spring_tasseled_cap()
            .add_summer_ndvi()
            .add_summer_savi()
            .add_summer_tasseled_cap()
            .add_fall_ndvi()
            .add_fall_savi()
            .add_fall_tasseled_cap()
            .transform()
        )
        return self


###############################################################################################


class RadarProcessor:
    def __init__(self, collection: ee.ImageCollection) -> None:
        self.collection = collection

    def select_bands(self, pattern: str) -> RadarProcessor:
        self.collection = self.collection.select(pattern)
        return self

    def apply_boxcar_filter(self):
        self.collection = self.collection.map(
            lambda image: image.convolve(ee.Kernel.square(1))
        )
        return self

    def add_ratio(self, b1, b2, name):
        self.collection = self.collection.map(Ratio(b1, b2, name))
        return self

    def transform(self) -> RadarProcessor:
        self.collection = self.collection.mosaic()
        return self


class S1Processor(RadarProcessor):
    def __init__(self, collection: ee.ImageCollection) -> None:
        super().__init__(collection)

    def process(self) -> S1Processor:
        self.select_bands("V.*").apply_boxcar_filter().add_ratio(
            "VV", "VH", "VV_VH"
        ).transform()
        return self


class ALOSProcessor(RadarProcessor):
    def __init__(self, start_date: str = None, end_date: str = None) -> None:
        super().__init__(ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH"))
        self.start_date = start_date or "2018"
        self.end_date = end_date or "2021"

    def filter_date(self) -> ALOSProcessor:
        self.collection = self.collection.filterDate(self.start_date, self.end_date)
        return self

    def transform(self) -> RadarProcessor:
        self.collection = self.collection.median()
        return self

    def process(self) -> ALOSProcessor:
        (
            self.select_bands("H.*")
            .apply_boxcar_filter()
            .add_ratio("HH", "HV", "HH_HV")
            .transform()
        )
        return self


## GAP AREA PROCESSOR
class GapAreaProcessor:
    def __init__(self, collection: ee.ImageCollection) -> None:
        self.collection = collection

    def __add__(self, other: GapAreaProcessor) -> GapAreaProcessor:
        self.collection = self.collection.merge(other.collection)
        return self

    def transform(self) -> GapAreaProcessor:
        self.collection = self.collection.median()
        return self

    def process(self) -> GapAreaProcessor:
        self.collection = self.collection.mosaic()
        return self


class S2GapProcessor(GapAreaProcessor):
    def __init__(self, start_date: str, end_date: str, region: ee.Geometry) -> None:
        super().__init__(ee.ImageCollection())
        self.start_date = start_date
        self.end_date = end_date

    def filter_date(self) -> S2GapProcessor:
        pass

    def mask_clouds(self) -> S2GapProcessor:
        pass

    def select_bands(self) -> S2GapProcessor:
        pass

    def add_ndvi(self) -> S2GapProcessor:
        pass

    def add_savi(self) -> S2GapProcessor:
        pass

    def add_tasseled_cap(self) -> S2GapProcessor:
        pass

    def process(self) -> S2GapProcessor:
        self.collection = self.collection.mosaic()
        return self


class S1GapProcessor(GapAreaProcessor):
    def __init__(self, collection: ee.ImageCollection) -> None:
        super().__init__(collection)

    def select_bands(self) -> S1GapProcessor:
        pass

    def denoise(self) -> S1GapProcessor:
        pass

    def add_ratio(self) -> S1GapProcessor:
        pass

    def process(self) -> S1GapProcessor:
        self.collection = self.collection.mosaic()
        return self


##
